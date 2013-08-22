import os
import sys
app_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(app_root, 'virtualenv.bundle.zip'))

import sae
from sae.ext.shell import ShellMiddleware
from app import app
app.debug = True
application = sae.create_wsgi_app(ShellMiddleware(app))
