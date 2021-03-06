#!/usr/bin/env python3

"""
Tamandua. Aggregate information from logfiles.

This is the main (entry point) of the web-app backend.
"""


import os
import sys

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASEDIR)

from flask import Flask
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

api.add_resource(rest_api.Columns,
                 '/columns',
                 resource_class_args=[dataFinder])

api.add_resource(rest_api.Tags,
                 '/tags',
                 resource_class_args=[dataFinder])

api.add_resource(rest_api.Search,
                 '/search/<int:page>/<int:size>',
                 resource_class_args=[dataFinder])

api.add_resource(rest_api.Count,
                 '/count',
                 resource_class_args=[dataFinder])

api.add_resource(rest_api.AdvancedCount,
                 '/advcount/<field>/<int:length>',
                 resource_class_args=[dataFinder])

api.add_resource(rest_api.AdvancedCount,
                 '/advcount/<field>/<int:length>/<separator>',
                 resource_class_args=[dataFinder],
                 endpoint='advcount_with_separator')

api.add_resource(rest_api.FieldChoices,
                 '/fieldchoices/<field>/<int:maxChoices>',
                 resource_class_args=[dataFinder],
                 endpoint='advcount')

api.add_resource(rest_api.SupportedFieldChoices,
                 '/supported_fieldchoices',
                 resource_class_args=[dataFinder])

api.add_resource(rest_api.Trend,
                 '/trend/<field>/<int:dataCount>',
                 resource_class_args=[dataFinder])

api.add_resource(rest_api.Trend,
                 '/trend/<field>/<int:dataCount>/<separator>',
                 resource_class_args=[dataFinder],
                 endpoint='trend_with_separator')

if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=True)
