from flask import Flask
from flask import request
from flask import render_template
import json
import pandas.io.sql as pdsql
from psycopg2 import connect

app = Flask(__name__)

def run_on_start():
	password = os.environ['roosje_pass']
    server = os.environ['aws_server']
    sql_dbname= 'shallots'
    conn = connect(database=self.sql_dbname, user ='postgres', \
                           password=password, host=server)
    cursor = conn.cursor()
    return [conn, cursor]

@app.route('/')
def index():


    return "hello!"

@app.route('/test')
def test():
	return render_template('viz_template.html', data=x )

if __name__ == '__main__':
    app.conn, app.cursor = run_on_start()
    app.run(host='0.0.0.0', port=6969, debug=True)