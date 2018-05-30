bind = 'unix:%(remote_folder)s/%(service)s/gunicorn.sock'
workers = 3
accesslog = '%(logs_folder)s/%(service)s/access.log'
errorlog = '%(logs_folder)s/%(service)s/error.log'
loglevel = 'debug'
proc_name = '%(service)s'
