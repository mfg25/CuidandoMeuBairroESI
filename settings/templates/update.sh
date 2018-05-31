#!/bin/bash

cd $(dirname $BASH_SOURCE)
%(venv_folder)s/bin/flask run_browser
%(venv_folder)s/bin/flask send_notifications
