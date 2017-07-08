#!/usr/bin/env python3

"""
Tamandua. Aggregate information from logfiles.

This is the main (entry point) of the web-app backend.
"""


import os
import sys

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASEDIR)

from flask import Flask, render_template
from flask_restful import Api

from src.web.data_finder import DataFinder
from src.config import Config
from src.constants import CONFIGFILE
from src.exceptions import print_exception
from src.web.exceptions import errors as api_errors
import src.web.rest_api as rest_api


app = Flask(
    __name__,
    template_folder='web/templates',
    static_folder='web/static')
api = Api(app, errors=api_errors)

Config().setup(os.path.join(BASEDIR, CONFIGFILE), BASEDIR)

try:
    dataFinder = DataFinder()
except Exception as e:
    print_exception(e, "Trying to create an instance of DataFinder", "Exiting application", fatal=True)
    sys.exit(1)


@app.route('/')
def home():
    return render_template('index.html', fieldnames=dataFinder.availableFields)


api.add_resource(rest_api.Columns, '/api/columns', resource_class_args=[dataFinder])
api.add_resource(rest_api.Tags, '/api/tags', resource_class_args=[dataFinder])
api.add_resource(rest_api.Search, '/api/search/<int:page>/<int:size>', resource_class_args=[dataFinder])
api.add_resource(rest_api.Count, '/api/count', resource_class_args=[dataFinder])
api.add_resource(rest_api.AdvancedCount, '/api/advcount/<int:length>', resource_class_args=[dataFinder])

if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=True)
