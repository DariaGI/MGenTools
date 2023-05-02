import csv

from flask import Flask, request, render_template, send_file, make_response, Response, jsonify
import pandas as pd
import polars as pl
from hadlers.Data import Data
from hadlers.keywordsClassifier import keywordsClassify
from hadlers.classifier import classifyFunctions
from hadlers.clsDisplay import displayClassification
from hadlers.counter import countFunctions
from hadlers.visualize_statistics import buildPlots
from hadlers.visualize_statistics import statistic_test
from hadlers.validator import validate
from hadlers.validator import validate_tree
from hadlers.memoryzip_plots import get_zip_buffer
from sys import getsizeof
import os
import io

from logging.config import dictConfig

import settings
from typing import List

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


app = Flask(__name__)
data = Data()
allowed_file_types = ['csv']

if data.getRastCls().shape[0] == 0:
    path_to_rast_classification = os.path.join(settings.ROOT_DIR, 'static/csvFiles/rastClassification.csv')
    data.setRastCls(pl.read_csv(path_to_rast_classification))

if getsizeof(data.getHierarchy):
    hierarchy = displayClassification(data)
    data.setHierarchy(hierarchy)

@app.route('/')
def index():
     return render_template("index.html")

@app.route('/analisis', methods=['get', 'post'])
def analyse():
    return render_template("analisis.html", dict=data.getClassified(), hierarchy=data.getHierarchy(), countTable=data.getCount(), plots=data.getPlots(), displayCount=1)

@app.route('/documentation', methods=['get'])
def documentation():
    return render_template("documentation.html")

# можно убрать
@app.route('/reset', methods=['post'])
def reset():
    data.reset()
    return render_template("analisisCls.html", dict=data.getClassified(), displayCount=1)


@app.route('/classify', methods=['post'])
def classify():
    # data.reset()
    cls_types = request.form.getlist('cls_type')
    rastDownloads = request.files.getlist("rastDownloads[]")
    userCls = request.files.get("userCls")

    errors = []
    if (userCls):
        errorUserCls, validated = validate(userCls, "userCls")
        data.setUserCls(validated)
        errors.append(errorUserCls)

    errorDownloads, validated = classifyFunctions(cls_types, rastDownloads, data)
    data.setClassified(validated)  
    errors.append(errorDownloads)

    return render_template("analisisCls.html", dict=data.getClassified(), displayCount=1, errors=errors)

@app.route('/fullClassified', methods=['get', 'post'])
def fullClassified():
    dict = data.getClassified()
    return render_template("fullClassified.html", dict=dict, displayCount=len(dict))


@app.route('/count', methods=['post'])
def count():
    data.setResCount()
    data.resComputedMatrix()
    request_json_data = request.get_json()
    data.setCount(countFunctions(data, request_json_data))

    return render_template("analisisCount.html", countTable=data.getCount())

@app.route('/visualize', methods=['post'])
def visualize():
    data.resPlots()

    random_state = 0
    dbscan_eps = 0.05
    if bool(request.form.get('bayesian_gaussian_mixture__input')):
        random_state = request.form.get('bayesian_gaussian_mixture__input')

    if bool(request.form.get("DBSCAN__input")):
        dbscan_eps = request.form.get("DBSCAN__input")


    params = dict(
        data=data,
        methods=request.form.getlist('method'),
        perplexity=request.form['perplexity'],
        clusterMethods=request.form.getlist('clusterMethod'),
        n_clusters=request.form['n_clusters'],
        linkage=request.form['linkage'],
        distance_metric=request.form["convergenceType"],
        random_state=random_state,
        eps=dbscan_eps,
        tree=request.files.get("unifrac_data__tree"),
        otu_ids=request.files.get("unifrac_data__otu")
    )
    
    data.setPlots(buildPlots(**params))
    
    return render_template("analisisVsl.html", plots=data.getPlots())

@app.route('/download/<type>/<filename>', methods=['get'])
def download(type, filename):
    if type == "classified":
        df = data.getClassified()[filename].write_csv(separator=";")
    if type == "kwClassification":
        df = data.getKwCls().write_csv(separator=";")
    if type == "counted":
        df = data.getCount().write_csv(separator=";")
    return Response(df,status=200,headers={"Content-disposition":"attachment; filename="+filename+".csv"}, mimetype="application/csv")



@app.route('/download/plots', methods=['get'])
def download_plots():
    export_format = request.args.get('export_format') # Получает формат для экспорта из query param
    buff = get_zip_buffer(data, export_format)
    with open("all_plots.zip", "wb") as outfile:
        # Copy the BytesIO stream to the output file
        outfile.write(buff.getbuffer())
    return send_file(buff, mimetype='application/zip', as_attachment=True, download_name="all_plots.zip")


@app.route('/uploadBreakdown', methods=['post'])
def uploadBreakdown():
    breakdown = request.files.get("breakdown")
    error, validated = validate(breakdown, 'breakdown')
    data.setBreakdown(validated)
    return  render_template("breakdown.html", df=data.getBreakdown(), error=error)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Проведение оценки статистической достоверности различий на странице анализа"""
    # return render_template('statistic_test.html', result={
    #     'anosim': {
    #         'method_name': 'anosim',
    #         'test_statistic_name': 'R',
    #         'sample_size': 30,
    #         'number_of_groups': 3,
    #         'test_statistic': 0.893477,
    #         'p_value': 0.001,
    #         'number_of_permutations': 999
    #     }
    # })

    random_state = 0
    dbscan_eps = 0.05
    if bool(request.form.get('bayesian_gaussian_mixture__input')):
        random_state = request.form.get('bayesian_gaussian_mixture__input')
    if bool(request.form.get("DBSCAN__input")):
        dbscan_eps = request.form.get("DBSCAN__input")

    distance_metric = request.form["convergenceType"]
    error=[]
    tree=None
    otu_ids=None
    if distance_metric in ["weighted_unifrac", "unweighted_unifrac"]:
        tree, otu_ids, error = validate_tree(tree_file=request.files.get("unifrac_data__tree"), otu_file=request.files.get("unifrac_data__otu"))

    if len(error) < 1:
        params = dict(
            data=data,
            statMethods=request.form.getlist('statMethod'),
            clusterMethods=request.form.getlist('clusterMethod'),
            distance_metric=distance_metric,
            n_clusters=request.form['n_clusters'],
            linkage=request.form['linkage'],
            tree=tree,
            otu_ids=otu_ids,
            random_state=random_state,
            eps=dbscan_eps
        )

        data.setStatResults(statistic_test(**params))

        return render_template('statistic_test.html', result=data.getStatResults())




if __name__ == "__main__":
    app.run(debug=settings.DEBUG)