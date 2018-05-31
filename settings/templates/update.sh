#!/bin/bash

cd $(dirname $BASH_SOURCE)
%(venv_folder)s/bin/flask update_data
%(venv_folder)s/bin/flask send_notifications
