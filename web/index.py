from flask import Flask
from flask import request
from flask import render_template
import json
import pandas.io.sql as pdsql
import psycopg2

app = Flask(__name__)

def run_on_start():
    conn = psycopg2.connect(dbname='***', user='postgres', host='/tmp')
    cursor = conn.cursor()
    return [conn, cursor]

@app.route('/')
def index():
    return "hello!"

if __name__ == '__main__':
    app.conn, app.cursor = run_on_start()
    app.run(host='0.0.0.0', port=6969, debug=True)