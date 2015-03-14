from flask import Flask
from flask import request
from flask import render_template
import json
import pandas as pd
import pandas.io.sql as psql
from psycopg2 import connect
from sqlalchemy import Table, MetaData, create_engine
import os
from math import ceil
from operator import itemgetter
import itertools
from collections import Counter
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
	sql_dbname= 'shallots'
	conn = connect(database=sql_dbname, user ='postgres', \
						   password=password, host=server)
	cursor = conn.cursor()
	engine = create_engine("postgresql://postgres:%s@%s/%s" \
					  %(password, server, sql_dbname))

	return [conn, cursor, engine]

@app.route('/')
def index():
	# CODE FOR MAP 
	alchcon = app.engine.connect().connection
	data = psql.read_sql("SELECT * from countries \
						  JOIN (SELECT legal, domain \
								FROM clusters JOIN \
								features ON \
								clusters.cluster_id=features.cluster_id) \
								AS leg \
						  ON countries.domain=leg.domain;", app.engine)
	datalst = []
	condition_leg = data['legal']==True
	for cntry in data.columns[1:-2]:
		condition_cntry = data[cntry]==True
		total = len(data[condition_cntry])
		legal = len(data[condition_cntry & condition_leg])
		datalst.append([cntry, round(float(legal)/total, 1)])
	# example: {Netherlands: 0.5}

	# CODE FOR PIECHART
	'''app.cursor.execute("SELECT cluster_name, cnt \
					FROM clusters JOIN (\
						SELECT cluster_id, COUNT(*) AS cnt \
						FROM features2 \
						GROUP BY cluster_id) AS cl \
					ON cl.cluster_id=clusters.cluster_id;")'''
	'''dataPie = psql.read_sql("SELECT cluster_id-1 as category, \
						ROUND(COUNT(*)*1.0/SUM(COUNT(*)) OVER(),2) AS measure \
						FROM features \
						GROUP BY cluster_id;", app.engine)
	print dataPie.head(15)
	dataPie.to_json('static/data/piedata.json', orient="records")'''

	# CODE FOR GRAPH
	# FOR NETWORK ON CLUSTERS
	'''dataNodes2 = psql.read_sql("SELECT clusters.cluster_id-1 AS tmp, size, \
								cluster_name AS name \
								FROM clusters JOIN \
								(SELECT cluster_id, \
								count(*) as size FROM features \
								GROUP BY cluster_id) AS cl \
								ON clusters.cluster_id = cl.cluster_id;", app.engine)
	dataNodes2['index'] = dataNodes2.index
	dataNodes2.rename(columns={'tmp':'group'}, inplace=True)
	dataNodes2 = dataNodes2.set_index('group')
	dataLinks2 = psql.read_sql("SELECT cluster_id-1 AS cluster_to, cluster_from, \
								COUNT(*) AS value \
								FROM features JOIN \
								(SELECT cluster_id-1 AS cluster_from, domain_to \
								FROM features JOIN relations \
								ON relations.domain_from = features.domain) AS prt1 \
								ON prt1.domain_to = features.domain \
								WHERE cluster_id-1 <> cluster_from \
								GROUP BY cluster_to, cluster_from;", app.engine)
	dataLinks2 = dataLinks2.join(dataNodes2['index'], on='cluster_from')
	dataLinks2.rename(columns={'index':'source'}, inplace=True)
	dataLinks2 = dataLinks2.join(dataNodes2['index'], on='cluster_to')
	dataLinks2.rename(columns={'index':'target'}, inplace=True)
	dataNodes2 = dataNodes2.reset_index()
	dataNodes2.to_json('static/data/nodes2.json', orient="records")
	dataLinks2.to_json('static/data/links2.json', orient="records")'''

	# WORDCLOUD DATA ALREADY PREPARED IN SHALLOTS.PY
	'''
	rx = re.compile('\W+')  
	data = psql.read_sql("SELECT cluster_id-1 AS cluster, text FROM features;", app.engine)
	data['text'] = data['text'].apply(lambda x: (clean_tokenized_text(x, rx)))
	data = data.groupby('cluster')['text'].apply(lambda x: \
						list(itertools.chain.from_iterable(x))).reset_index()
	for i, row in data.iterrows():
		c = Counter(row['text'])
		filename = 'static/data/worddata'+str(i)+'.json'
		json.dump(c.most_common(50), open(filename, 'wb'))
	'''
	return render_template('dashboard.html', datamap=datalst)

def set_default(obj):
	if isinstance(obj, set):
		return list(obj)
	raise TypeError


# FUTURE: 
# concept graph per cluster
# piechart clusters per country


if __name__ == '__main__':
	app.conn, app.cursor, app.engine = run_on_start()
	print "done"
	app.run(host='0.0.0.0', port=8080, debug=True)
	app.cursor.close()
	app.conn.close()