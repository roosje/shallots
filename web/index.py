from flask import Flask
from flask import render_template
import json
import pandas as pd
import pandas.io.sql as psql
from sqlalchemy import Table, MetaData, create_engine
import os
from operator import itemgetter
import itertools
from collections import Counter, defaultdict
import re
import numpy as np
import sys
sys.path.append("..")
from clean_tokenize import *

app = Flask(__name__)
app._static_folder = 'static'


def run_on_start():
    password = os.environ['roosje_pass']
    server = os.environ['aws_server']
    sql_dbname = 'shallots'
    engine = create_engine("postgresql://postgres:%s@%s/%s"
                           % (password, server, sql_dbname))
    return engine


@app.route('/')
def index():
    # CODE FOR MAP
    alchcon = app.engine.connect().connection
    data = psql.read_sql("SELECT * from countries \
                          JOIN (SELECT legal, clusters.cluster_id, \
                                domain \
                                FROM clusters JOIN \
                                features ON \
                                clusters.cluster_id=features.cluster_id) \
                                AS leg \
                          ON countries.domain=leg.domain;", app.engine)
    datalst = []
    data_pies = defaultdict(list)
    condition_leg = data['legal'] == True
    condition_illeg = data['legal'] == False
    for cntry in data.columns[1:-3]:
        condition_cntry = data[cntry] == True
        sumcountry = len(data[condition_cntry])
        total = len(data[condition_cntry & (condition_leg | condition_illeg)])
        legal = len(data[condition_cntry & condition_leg])
        if total > 0:
            datalst.append([cntry, round(float(legal)/total, 1)])
        # example: {Netherlands: 0.5}
        for cl in data['cluster_id'].unique():
            temp = {}
            condition_clst = data['cluster_id'] == cl
            total2 = len(data[condition_cntry & condition_clst])
            if total2 > 0:
                temp['value'] = total2
                temp['label'] = cl
                data_pies[cntry].append(temp)

    # CODE FOR CLUSTER_NAMES WITH CLUSTER_IDs ALREADY PREPARED IN SHALLOTS.PY
    # CODE FOR PIECHART DATA ALREADY PREPARED IN SHALLOTS.PY
    # CODE FOR GRAPH DATA ALREADY PREPARED IN SHALLOTS.PY
    # WORDCLOUD DATA ALREADY PREPARED IN SHALLOTS.PY

    names = psql.read_sql("SELECT cluster_id, cluster_name from clusters;",
                          app.engine)
    namelst = {}
    for row in names.iterrows():
        row = row[1]
        namelst[row['cluster_id']] = row['cluster_name']
    return render_template('dashboard.html', datamap=datalst,
                           clnames=json.dumps(namelst),
                           mappies=json.dumps(data_pies))


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

if __name__ == '__main__':
    app.engine = run_on_start()
    print "done"
    app.run(host='0.0.0.0', port=8080, debug=True)
