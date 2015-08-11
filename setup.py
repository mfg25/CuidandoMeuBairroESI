#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name="viratoken",
    version='0.0.1',
    # url='',
    description='Small lib to encode/decode/sign/verify JWTs '
                'using asymmetric cryptography.',
    author='Andrés M. R. Martano',
    # author_email='',
    packages=["viratoken"],
    install_requires=[
        'cryptography',
        'pyjwt',
    ],
    # classifiers=[
    # ]
)
