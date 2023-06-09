from sklearn.mixture import BayesianGaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.decomposition import PCA
from sklearn.manifold import MDS, TSNE
import pandas as pd
import polars as pl
import plotly
import plotly.express as px
import json
import numpy as np
try:
    from skbio.diversity import beta_diversity
    from skbio.stats.distance import anosim
    from skbio.stats.distance import permanova
except ImportError:
    print("!ERROR! Could not import skbio ")

# from rpy2.robjects import pandas2ri, r, DataFrame
# from rpy2.robjects.packages import importr
# import rpy2.rinterface as ri
# ri.initr()
# pandas2ri.activate()


def clusterization(data, clusterMethods, eps=0.05, n_clusters="2", linkage='ward', distance_metric='euclidean',
                   random_state=None, tree=None, otu_ids=None):
    genes_count = data.getCount()
    distance_matrix = data.getComputedMatrix()
    print(otu_ids)
    print(tree)
    predictions = []

    if distance_metric == 'euclidean' and distance_metric not in distance_matrix:
        x = precomputed_matrix(genes_count, distance_metric)
        distance_matrix['euclidean'] = x

    else:
        if len(clusterMethods) > 0 and distance_metric not in distance_matrix:
            dist_matrix = precomputed_matrix(genes_count, distance_metric=distance_metric, tree=tree, otu_ids=otu_ids)
            distance_matrix[distance_metric] = dist_matrix

        if len(clusterMethods) > 0 and ("k_avg" in clusterMethods or 'bayesian_gaussian_mixture' in clusterMethods) \
                    and 'euclidean' not in distance_matrix:
                eucl_matrix = precomputed_matrix(genes_count, distance_metric='euclidean')
                distance_matrix['euclidean'] = eucl_matrix

        if len(clusterMethods) < 1 and distance_metric not in distance_matrix:
            eucl_matrix = precomputed_matrix(genes_count, distance_metric='euclidean')
            distance_matrix['euclidean'] = eucl_matrix
            dist_matrix = precomputed_matrix(genes_count, distance_metric=distance_metric, tree=tree, otu_ids=otu_ids)
            distance_matrix[distance_metric] = dist_matrix

    if 'k_avg' in clusterMethods:
        # print("KMeans")
        model = KMeans(n_clusters=int(n_clusters), n_init='auto')
        calc_matrix = np.array([*distance_matrix["euclidean"]])
        model.fit(calc_matrix)
        predictions = model.predict(calc_matrix)

    elif 'bayesian_gaussian_mixture' in clusterMethods:
        # print("BayesianGaussianMixture")
        model = BayesianGaussianMixture(n_components=int(n_clusters), random_state=int(random_state), covariance_type="full")
        calc_matrix = np.array([*distance_matrix["euclidean"]])
        model.fit(calc_matrix)
        predictions = model.predict(calc_matrix)

    elif 'hierarchical_clustering' in clusterMethods:
        if linkage == "ward":
            # print("AgglomerativeClustering")
            model = AgglomerativeClustering(n_clusters=int(n_clusters), metric="euclidean", linkage=linkage)
            calc_matrix = np.array([*distance_matrix["euclidean"]])
            model.fit_predict(calc_matrix)
            predictions = model.labels_
        elif linkage != "ward":
            model = AgglomerativeClustering(n_clusters=int(n_clusters), metric="precomputed", linkage=linkage)
            calc_matrix = np.array([*distance_matrix[distance_metric]])
            model.fit_predict(calc_matrix)
            predictions = model.labels_

    elif 'DBSCAN' in clusterMethods:
        # print("AffinityPropagation")
        model = DBSCAN(eps=float(eps), min_samples=3, metric='precomputed')
        calc_matrix = np.array([*distance_matrix[distance_metric]])
        model.fit(calc_matrix)
        predictions = model.labels_

    data.setComputedMatrix(distance_matrix)

    return distance_matrix, predictions


def precomputed_matrix(genes_count, distance_metric='euclidean', tree=None, otu_ids=None):
    bc_dm = []
    strains = genes_count["Strain"]
    #for old version of skbio
    # features = genes_count.columns[1:]
    # genes_count_cut = np.swapaxes(np.array(genes_count[features]), 0, 1)
    genes_count_cut = np.array(genes_count[:, 1:])
    bc_dm = beta_diversity(distance_metric, genes_count_cut, strains)




    return bc_dm


def statistic_test(data, statMethods, clusterMethods, eps=0.05, distance_metric='euclidean', n_clusters="2",
                   linkage='ward',
                   tree=None, otu_ids=None, random_state=None):
    genes_count = data.getCount()
    test_result = {}
    errors = []


    if genes_count.is_empty():
        errors.append("данные не выбраны")
        return errors, test_result

    strains = genes_count["Strain"]

    if len(strains) > 1:

        distance_matrix, predictions = clusterization(data, clusterMethods=clusterMethods,
                                                      distance_metric=distance_metric, eps=eps, n_clusters=n_clusters,
                                                      linkage=linkage,
                                                      random_state=random_state, tree=tree, otu_ids=otu_ids)
        sample_md = pd.DataFrame(predictions, index=list(strains), columns=["subject"])
        if len(set(predictions)) > 1:
            if 'anosim' in statMethods:
                anosim_result = [*anosim(distance_matrix[distance_metric], sample_md, column='subject', permutations=999)]
                anosim_result[4] = round(anosim_result[4], 3)
                test_result["ANOSIM"] = anosim_result
            if 'permanova' in statMethods:
                permanova_result = [*permanova(distance_matrix[distance_metric], sample_md, column='subject', permutations=999)]
                permanova_result[4] = round(permanova_result[4], 3)
                test_result["PERMANOVA"] = permanova_result

        else:
            errors.append("Кластеры в выборке не были выявлены с помощью данного типа кластеризации, попробуйте другой метод.")

        return errors, test_result

    else:
        test_result["Too few strains selected"] = []
        return test_result, errors


def match(table_to, table_from):
    for rowIndex, row in table_to.iterrows():
        strain = row['Strain']
        table_from_indexes = table_from.filter(pl.col("Strain") == strain)
        if (len(table_from_indexes)) > 0:
            table_to.loc[(rowIndex, 'Breakdown Type')] = table_from_indexes[0, 'Breakdown Type'].strip()


def buildScatter(data, components, predictions):
    genes_count = data.getCount()
    components["Strain"] = genes_count["Strain"]
    components['Breakdown Type'] = 'unknown'

    if not data.getBreakdown().is_empty():
        match(components, data.getBreakdown())

    if len(predictions) > 0:
        components['Cluster'] = predictions
        components["Cluster"] = 'Cluster # ' + components["Cluster"].astype(str)

    else:
        components['Cluster'] = 'not predicted'

    def improve_text_position(x):
        """ it is more efficient if the x values are sorted """
        # fix indentation
        positions = ['top center', 'bottom center']  # you can add more: left center ...
        return [positions[i % len(positions)] for i in range(len(x))]

    fig = px.scatter(components, x='Component 1', y='Component 2', color='Cluster', symbol='Breakdown Type',
                     text='Strain', color_discrete_sequence=px.colors.qualitative.Dark24)
    fig.layout = plotly.graph_objects.Layout(plot_bgcolor='#ffffff', width=900, height=700)

    # fig.update_traces(textposition='top left', marker_size=10)
    fig.update_traces(textposition=improve_text_position(components['Component 1']), marker_size=10)

    pltJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return pltJSON


def buildPlots(data, methods, clusterMethods, eps=0.05, perplexity="2", n_clusters='2', linkage='ward',
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
                distance_matrix, predictions = clusterization(data, clusterMethods=clusterMethods, eps=eps,
                                                              n_clusters=n_clusters,
                                                              linkage=linkage, distance_metric=distance_metric,
                                                              random_state=int(random_state), tree=tree,
                                                              otu_ids=otu_ids)
                t_sne_init = "pca"
            else:
                if "pca" in methods:
                    # print("cannot precomputed matrix for plots, all switched to euclidean")
                    distance_matrix, predictions = clusterization(data, clusterMethods=clusterMethods, eps=eps,
                                                                  n_clusters=n_clusters, linkage=linkage,
                                                                  distance_metric='euclidean',
                                                                  random_state=int(random_state), tree=tree,
                                                                  otu_ids=otu_ids)

                if 'mds' in methods or "t_sne" in methods:
                    distance_matrix, predictions = clusterization(data, clusterMethods=clusterMethods, eps=eps,
                                                                  n_clusters=n_clusters,
                                                                  linkage=linkage, distance_metric=distance_metric,
                                                                  random_state=int(random_state), tree=tree,
                                                                  otu_ids=otu_ids)
                    t_sne_init = "random"

            if 'pca' in methods:
                # only eucledian distance
                methodData = PCA(n_components=2, random_state=0)
                x = np.array([*distance_matrix["euclidean"]])
                components = pd.DataFrame(data=methodData.fit_transform(x), columns=['Component 1', 'Component 2'])
                plots['PCA'] = buildScatter(data, components, predictions)

            if 'mds' in methods:
                methodData = MDS(random_state=0, dissimilarity="precomputed", normalized_stress="auto")
                x = np.array([*distance_matrix[distance_metric]])
                components = pd.DataFrame(data=methodData.fit_transform(x), columns=['Component 1', 'Component 2'])
                plots['MDS'] = buildScatter(data, components, predictions)
            #     vegan = importr("vegan")
            #     x = np.array([*distance_matrix[distance_metric]])
            #     methodData = vegan.metaMDS(x, k=2)
            #     MDS_scores = r.scores(methodData)
            #     components = pd.DataFrame({'Component_1': MDS_scores[:, 0], 'Component_2': MDS_scores[:, 1]})
            #     plots['NMDS'] = buildScatter(data, components, predictions)

            if 't_sne' in methods:
                methodData = TSNE(random_state=0, perplexity=float(perplexity), metric="precomputed", init=t_sne_init)
                x = np.array([*distance_matrix[distance_metric]])
                components = pd.DataFrame(data=methodData.fit_transform(x), columns=['Component 1', 'Component 2'])
                plots['t-SNE'] = buildScatter(data, components, predictions)

        else:
            x = []
            y = []
            for value in genes_count[:, features].to_numpy:
                x.append(value[0])
                y.append(0)

            components = pd.DataFrame(data={'Component 1': x, 'Component 2': y})

            plots['No method'] = buildScatter(data, components, strains)

    return plots
