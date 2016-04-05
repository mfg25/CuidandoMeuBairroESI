from __future__ import unicode_literals  # unicode by default
import os

DEBUG = False
# DEBUG_TB_INTERCEPT_REDIRECTS = False

SQLALCHEMY_DATABASE_URI = (
    'postgresql://{user}:{password}@{host}:{port}/{db_name}'
    .format(
        user=os.environ['OPENSHIFT_POSTGRESQL_DB_USERNAME'],
        password=os.environ['OPENSHIFT_POSTGRESQL_DB_PASSWORD'],
        host=os.environ['OPENSHIFT_POSTGRESQL_DB_HOST'],
        port=os.environ['OPENSHIFT_POSTGRESQL_DB_PORT'],
        db_name=os.environ['OPENSHIFT_APP_NAME']))

# INSTANCE_FOLDER_PATH = "/blah/instance"
SQLALCHEMY_TRACK_MODIFICATIONS = False
