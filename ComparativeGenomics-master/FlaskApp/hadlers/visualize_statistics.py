from sklearn.mixture import BayesianGaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, AffinityPropagation
from sklearn.decomposition import PCA
from sklearn.manifold import MDS, TSNE
import pandas as pd
import polars as pl
import plotly
import plotly.express as px
import json
import numpy as np
from skbio.diversity import beta_diversity
from skbio.stats.distance import anosim
from skbio.stats.distance import permanova



def clusterization(data, clusterMethods, n_clusters="2", linkage='ward', distance_metric='euclidean',
                   random_state=None, tree=None, otu_ids=None):

    genes_count = data.getCount()
    distance_matrix = data.getCumputedMatrix()
    print(distance_matrix.keys())
    predictions = []

    if distance_metric == 'euclidean' and distance_metric not in distance_matrix:
            x = precomputed_matrix(genes_count, distance_metric)
            distance_matrix['euclidean'] = x

    else:
        if ("0" in clusterMethods or "3" in clusterMethods) and 'euclidean' not in distance_matrix and distance_metric not in distance_matrix:
            print("cannot precomputed")
            eucl_matrix = precomputed_matrix(genes_count, distance_metric='euclidean')
            distance_matrix['euclidean'] = eucl_matrix
            dist_matrix = precomputed_matrix(genes_count, distance_metric=distance_metric)
            distance_matrix[distance_metric] = dist_matrix

        elif ("1" in clusterMethods or "2" in clusterMethods) and distance_metric not in distance_matrix:
            print("precomputed")
            x = precomputed_matrix(genes_count, distance_metric=distance_metric, tree=tree, otu_ids=otu_ids)
            distance_matrix[distance_metric] = x

        elif len(clusterMethods) < 1 and distance_metric not in distance_matrix:
            eucl_matrix = precomputed_matrix(genes_count, distance_metric='euclidean')
            distance_matrix['euclidean'] = eucl_matrix
            dist_matrix = precomputed_matrix(genes_count, distance_metric=distance_metric)
            distance_matrix[distance_metric] = dist_matrix

    if '0' in clusterMethods:
        print("KMeans")
        model = KMeans(n_clusters=int(n_clusters), n_init='auto')
        calc_matrix = np.array([*distance_matrix["euclidean"]])
        model.fit(calc_matrix)
        predictions = model.predict(calc_matrix)

    elif '3' in clusterMethods:
        print("BayesianGaussianMixture")
        model = BayesianGaussianMixture(n_components=int(n_clusters), random_state=random_state)
        calc_matrix = np.array([*distance_matrix["euclidean"]])
        model.fit(calc_matrix)
        predictions = model.predict(calc_matrix)

    elif '1' in clusterMethods and linkage != "ward":
        print("AgglomerativeClustering")
        model = AgglomerativeClustering(n_clusters=int(n_clusters), metric="precomputed", linkage=linkage)
        calc_matrix = np.array([*distance_matrix[distance_metric]])
        model.fit_predict(calc_matrix)
        predictions = model.labels_

    elif '2' in clusterMethods:
        print("AffinityPropagation")
        model = AffinityPropagation(affinity='precomputed', random_state=random_state)
        calc_matrix = np.array([*distance_matrix[distance_metric]])
        model.fit(calc_matrix)
        predictions = model.labels_

    data.setCumputedMatrix(distance_matrix)
    return distance_matrix, predictions


def precomputed_matrix(genes_count, distance_metric='euclidean', tree=None, otu_ids=None):
    bc_dm = []

    strains = genes_count["Strain"]
    features = genes_count.columns[1:]
    genes_count_cut = np.swapaxes(np.array(genes_count[features]), 0, 1)

    if distance_metric in ["euclidean", "braycurtis", "jaccard"]:
        bc_dm = beta_diversity(distance_metric, genes_count_cut, strains)
    elif distance_metric in ["weighted_unifrac", "unweighted_unifrac"]:
        bc_dm = beta_diversity(distance_metric, genes_count_cut, strains, tree=tree, otu_ids=otu_ids)

    return bc_dm



def statistic_test(data, distance_metric, statMethods, clusterMethods, n_clusters="2", linkage='ward',
                   tree=None, otu_ids=None, random_state=None):
    genes_count = data.getCount()
    test_result = {}

    if genes_count.is_empty():
        test_result["No data selected"] = []
        return test_result

    strains = genes_count["Strain"]

    if len(strains) > 1:
        distance_matrix, predictions = clusterization(data, clusterMethods=clusterMethods, distance_metric=distance_metric, n_clusters=n_clusters, linkage=linkage,
                                                           random_state=random_state, tree=tree, otu_ids=otu_ids)
        sample_md = pd.DataFrame(predictions, index=list(strains), columns=["subject"])
        if '0' in statMethods:
            test_result["ANOSIM"] = anosim(distance_matrix[distance_metric], sample_md, column='subject', permutations=999)
        if '1' in statMethods:
            test_result["PERMANOVA"] = permanova(distance_matrix[distance_metric], sample_md, column='subject', permutations=999)

        return test_result

    else:
        test_result["Too few strains selected"] = []
        return test_result




def match(table_to, table_from):
    for rowIndex, row in table_to.iterrows():
        strain = row['Strain']
        table_from_indexes = table_from.filter(pl.col("Strain") == strain)
        if (len(table_from_indexes)) > 0:
            table_to.loc[(rowIndex, 'Breakdown Type')] = table_from_indexes[0, 'Breakdown Type'].strip()



def buildScatter(data, components, predictions):
    components["Strain"] = data["Strain"]
    components['Breakdown Type'] = 'unknown'

    if not data.getBreakdown().is_empty():
        match(components, data.getBreakdown())

    if len(predictions) > 0:
        components['Cluster'] = predictions
        components["Cluster"] = 'Cluster # ' + components["Cluster"].astype(str)

    else:
        components['Cluster'] = 'not predicted'

    fig = px.scatter(components, x='Component 1', y='Component 2', color='Cluster', symbol='Breakdown Type',
                     text='Strain', color_discrete_sequence=px.colors.qualitative.Dark24)
    fig.layout = plotly.graph_objects.Layout(plot_bgcolor='#ffffff', width=700, height=500)
    fig.update_traces(textposition='top left', marker_size=10)

    pltJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return pltJSON


def buildPlots(data, methods, clusterMethods, perplexity="10", n_clusters='2', linkage='ward',
               distance_metric='euclidean', tree=None, otu_ids=None, random_state=None):
    plots = {}
    genes_count = data.getCount()
    genes_count = genes_count[[s.name for s in genes_count if not (s.null_count() == genes_count.height)]]
    if genes_count.is_empty():
        return plots

    strains = genes_count["Strain"]
    features = genes_count.columns[1:]
    predictions = []

    if len(strains) > 1:
        if len(features) > 1:
            if distance_metric == "eucledian":
                distance_matrix, predictions = clusterization(data, clusterMethods=clusterMethods, n_clusters=n_clusters,
                                                linkage=linkage, distance_metric=distance_metric,
                                                random_state=random_state, tree=tree, otu_ids=otu_ids)
                t_sne_init = "pca"
            else:
                if "0" in methods:
                    print("cannot precomputed matrix for plots, all switched to euclidean")
                    distance_matrix, predictions = clusterization(data, clusterMethods=clusterMethods,
                                                    n_clusters=n_clusters, linkage=linkage, distance_metric='euclidean',
                                                    random_state=random_state, tree=tree, otu_ids=otu_ids)


                if '1' in methods or "2" in methods:
                    distance_matrix, predictions = clusterization(data, clusterMethods=clusterMethods, n_clusters=n_clusters,
                                                    linkage=linkage, distance_metric=distance_metric,
                                                    random_state=random_state, tree=tree, otu_ids=otu_ids)
                    t_sne_init = "random"


            if '0' in methods:
                # only eucledian distance
                methodData = PCA(n_components=2, random_state=0)
                x = np.array([*distance_matrix["euclidean"]])
                components = pd.DataFrame(data=methodData.fit_transform(x), columns=['Component 1', 'Component 2'])
                plots['PCA'] = buildScatter(genes_count, components, predictions)

            if '1' in methods:
                methodData = MDS(random_state=0, dissimilarity="precomputed", normalized_stress="auto")
                x = np.array([*distance_matrix[distance_metric]])
                components = pd.DataFrame(data=methodData.fit_transform(x), columns=['Component 1', 'Component 2'])
                plots['MDS'] = buildScatter(genes_count, components, predictions)

            if '2' in methods:
                methodData = TSNE(random_state=0, perplexity=float(perplexity), metric="precomputed", init=t_sne_init)
                x = np.array([*distance_matrix[distance_metric]])
                components = pd.DataFrame(data=methodData.fit_transform(x), columns=['Component 1', 'Component 2'])
                plots['t-SNE'] = buildScatter(genes_count, components, predictions)

        else:
            x = []
            y = []
            for value in genes_count[:, features].to_numpy:
                x.append(value[0])
                y.append(0)

            components = pd.DataFrame(data={'Component 1': x, 'Component 2': y})

            plots['No method'] = buildScatter(data, components, strains)

    return plots
