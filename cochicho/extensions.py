#!/usr/bin/env python
# coding: utf-8

from flask_sqlalchemy import SQLAlchemy

from cuidando_utils import SignerVerifier


db = SQLAlchemy()
sv = SignerVerifier()
