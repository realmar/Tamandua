#!/usr/bin/env python3

"""
Tamandua. Aggregate information from logfiles.

This is the main (entry point) of the web-app backend.
"""


import os
import sys

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASEDIR)

from flask import Flask, render_template, jsonify, request

from lib.web.data_finder import DataFinder
from lib.config import Config
from lib.constants import CONFIGFILE

app = Flask(
    __name__,
    template_folder='web/templates',
    static_folder='web/static')

config = Config(os.path.join(BASEDIR, CONFIGFILE), BASEDIR)
dataFinder = DataFinder(config)


def final_filter(data : dict, d: dict) -> dict:
    onlyImportant = d.get('only_important')

    if isinstance(onlyImportant, str):
        onlyImportant = onlyImportant.lower() in ('yes', 'true', '1')
    else:
        onlyImportant = False

    if onlyImportant:
        return dataFinder.filter_important(data)

    return data

@app.route('/')
def home():
    return render_template('index.html', fieldnames=dataFinder.availableFields)

# API

@app.route('/api/search', methods=['POST'])
def search():
    expression = request.get_json()

    if expression is None:
        return jsonify({})

    """
    # for debugging
    expression = {
        'fields' : [
            { 'sender': 'lionel' }
        ],

        "datetime": {
            "start": "2017/01/19 22:51:45",
            "end": "2017/01/19 22:55:50"
        }
        
        "only_important": "true|false"
    }
    """

    data = dataFinder.search(expression)
    return jsonify(final_filter(data, expression))

@app.route('/api/get/all')
def get_all():
    data = dataFinder.get_all()
    return jsonify(final_filter(data, request.args))

@app.route('/api/get/sample')
def get_sample():
    data = dataFinder.get_sample()
    return jsonify(final_filter(data, request.args))

if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=True)