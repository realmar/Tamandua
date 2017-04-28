# wsgi which can be used within apache2

import os
import sys

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASEDIR)

from tamandua_web import app as application