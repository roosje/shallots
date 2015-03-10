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

app = Flask(__name__)

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
	return "hello!"

@app.route('/graph')
def graph():
	app.cursor.execute("SELECT * FROM relations LIMIT 20;")
	data_rel = app.cursor.fetchall()
	app.cursor.execute("SELECT domain \
						FROM features")
	data_nodes = app.cursor.fetchall()
	return render_template('graph_temp.html', nodes=data_nodes, rels=data_rel)


@app.route('/map')
def map():
	#map : per country, count legal/illegal
	alchcon = app.engine.connect().connection
	data = psql.read_sql("SELECT * from countries \
						  JOIN (SELECT legal, domain \
								FROM clusters JOIN \
								features ON \
								clusters.cluster_id=features.cluster_id) \
								AS leg \
						  ON countries.domain=leg.domain;", app.engine)
	print data.columns
	datadict = {}
	condition_leg = data['legal']==True
	for cntry in data.columns[2:]:
		condition_cntry = data[cntry]==True
		total = data[condition_cntry].count()
		legal = data[condition_cntry & condition_leg].count()
		datadict[cntry] = float(legal)/total
	# example: {Netherlands: 0.5}
	return render_template('map_template.html', data=json.dumps(datadict))


@app.route('/test')
def test():
	#bar chart count domains per cluster name
	'''app.cursor.execute("SELECT cluster_name, cnt \
					FROM clusters JOIN (\
						SELECT cluster_id, COUNT(*) AS cnt \
						FROM features2 \
						GROUP BY cluster_id) AS cl \
					ON cl.cluster_id=clusters.cluster_id;")'''
	app.cursor.execute("SELECT cluster_id, COUNT(*) AS cnt \
						FROM features \
						GROUP BY cluster_id;")
	data_clcounts = app.cursor.fetchall()
	data = []
	total = 0
	for row in data_clcounts:
		total += row[1]
	for row in data_clcounts:
		data.append([ceil(float(row[1])/total*1000), row[1], row[0]])
	data = sorted(data, key=itemgetter(1)) 

	#graph : relations and cluster_names
	#app.cursor.execute("SELECT * FROM relations LIMIT 20;")
	#data_rel = app.cursor.fetchall()

	#map : per country, count legal/illegal
	#complicated querie on features and clusters table
	#app.cursor.execute("SELECT * FROM features2 LIMIT 20;")
	#data_map = app.cursor.fetchall()

	#x=zip(data_clcounts, data_rel)
	return render_template('viz_template.html', data=data)

# FUTURE: 
# wordcloud per cluster
# concept graph per cluster
# piechart clusters per country


if __name__ == '__main__':
	app.conn, app.cursor, app.engine = run_on_start()
	app.run(host='0.0.0.0', port=6969, debug=True)