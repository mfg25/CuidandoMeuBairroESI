#!/usr/bin/env python
# coding: utf-8

import os

from flask import Flask
from flask_cors import CORS
from flask_restplus import apidoc
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from cuidando_utils import SignerVerifier

from cochicho.views import api
from cochicho.sender import send_all
from cochicho.extensions import sv, db


def create_app(settings_folder):
    # App
    app = Flask(__name__)
    app.config.from_pyfile(
        os.path.join('..', 'settings', 'common.py'), silent=False)
    app.config.from_pyfile(
        os.path.join(settings_folder, 'local_settings.py'), silent=False)
    CORS(app, resources={r"*": {"origins": "*"}})

    # DB
    db.init_app(app)
    app.db = db

    # Signer/Verifier
    if app.config.get('PUBLIC_KEY_PATH'):
        pub_key_path = app.config['PUBLIC_KEY_PATH']
    else:
        pub_key_path = os.path.join(settings_folder, 'keypub')
    sv.config(pub_key_path=pub_key_path)
    app.sv = sv

    # API
    api.init_app(app)
    app.register_blueprint(apidoc.apidoc)
    # api.app = app
    # api.sv = sv

    # Mail
    app.mail = Mail(app)

    @app.cli.command()
    def init_db():
        '''Clear the existing data and create new tables.'''
        db.create_all()

    @app.cli.command()
    def send_messages():
        '''Send all messages.'''
        send_all(api)

    return app
