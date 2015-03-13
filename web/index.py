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
	dataPie = psql.read_sql("SELECT cluster_id-1 as category, \
						ROUND(COUNT(*)*1.0/SUM(COUNT(*)) OVER(),2) AS measure \
						FROM features \
						GROUP BY cluster_id;", app.engine)
	#print dataPie.head()
	dataPie.to_json('static/data/piedata.json', orient="records")

	# CODE FOR GRAPH
	dataNodes = psql.read_sql("SELECT cluster_id-1 as index2, domain \
						FROM features", app.engine)
	dataNodes['group'] = pd.Series(np.random.randint(1,16, size=len(dataNodes)))
	dataNodes['size'] = pd.Series(np.random.randint(1, 101, size=len(dataNodes)))
	dataNodes['index'] = dataNodes.index
	#dataNodes.rename(columns={'cluster_id':'index'}, inplace=True)
	dataNodes = dataNodes.set_index('domain')
	dataLinks = psql.read_sql("SELECT * FROM relations;", app.engine)
	dataLinks['value']= pd.Series(np.random.randint(1, 6, size=len(dataLinks)))
	dataLinks = dataLinks.join(dataNodes['index'], on='domain_from')
	dataLinks.rename(columns={'index':'source'}, inplace=True)
	dataLinks = dataLinks.join(dataNodes['index'], on='domain_to')
	dataLinks.rename(columns={'index':'target'}, inplace=True)
	dataNodes = dataNodes.reset_index()
	dataNodes.to_json('static/data/nodes.json', orient="records")
	dataLinks.to_json('static/data/links.json', orient="records")

	# WORDCLOUD DATA ALREADY PREPARED IN SHALLOTS.PY

	return render_template('dashboard.html', datamap=datalst)

@app.route('/graph')
def graph():
	app.cursor.execute("SELECT * FROM relations;")
	data_rel = app.cursor.fetchall()
	app.cursor.execute("SELECT domain \
						FROM features")
	data_nodes = app.cursor.fetchall()
	#data = {"nodes": [{"domain": "n[0]", "group":1 for n in data_nodes}], \
	#		"linkes": [{"source": }]}

	#with open('data/graphdata.json', 'w') as outfile:
    #	json.dump(data, outfile)
	return render_template('graph_temp.html')

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

@app.route('/graph2')
def graph2():
	dataNodes = psql.read_sql("SELECT domain \
						FROM features", app.engine)
	dataNodes['group'] = pd.Series(np.random.randint(1,16, size=len(dataNodes)))
	dataNodes['size'] = pd.Series(np.random.randint(1, 101, size=len(dataNodes)))
	dataNodes['index'] = dataNodes.index
	dataNodes = dataNodes.set_index('domain')
	dataLinks = psql.read_sql("SELECT * FROM relations;", app.engine)
	dataLinks['value']= pd.Series(np.random.randint(1, 6, size=len(dataLinks)))
	dataLinks = dataLinks.join(dataNodes['index'], on='domain_from')
	dataLinks.rename(columns={'index':'source'}, inplace=True)
	dataLinks = dataLinks.join(dataNodes['index'], on='domain_to')
	dataLinks.rename(columns={'index':'target'}, inplace=True)
	dataNodes = dataNodes.reset_index()
	dataNodes.to_json('static/data/nodes.json', orient="records")
	dataLinks.to_json('static/data/links.json', orient="records")
	#with open('data/links.json', 'w') as outfile:
	#	json.dump(dataLinks.to_json, outfile)
	return render_template('graph2.html')


# FUTURE: 
# wordcloud per cluster
# concept graph per cluster
# piechart clusters per country


if __name__ == '__main__':
	app.conn, app.cursor, app.engine = run_on_start()
	print "done"
	app.run(host='0.0.0.0', port=6969, debug=True)
	app.cursor.close()
	app.conn.close()