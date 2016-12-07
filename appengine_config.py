import os
from google.appengine.ext import vendor

# Add the correct packages path if running on Production
# (this is set by Google when running on GAE in the cloud)
if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    vendor.add('venv/lib/python2.7/site-packages')
