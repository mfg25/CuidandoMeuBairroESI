# -*- coding: utf-8 -*-

# http://docs.fabfile.org/en/1.5/tutorial.html

# from fabric.api import *
import os
from fabric.api import local, put, run, cd, env, prefix, task
# from fabric.network import ssh
# from flask.ext.script import Manager

# project = "gastosabertos"

# remote_project_dir = '/home/gastosabertos/gastos_abertos'
# remote_prefix = "source /home/gastosabertos/.virtualenvs/ga/bin/activate"

# env.user = 'gastosabertos'
# env.hosts = ['gastosabertos.org']
# # env.key_filename = '~/.ssh/ga_id_rsa'

# env.place = "remote"


# def smart_run(command, inside_env=False):
#     if env.place == "local":
#         local(command)
#     elif env.place == "remote":
#         if inside_env:
#             with cd(remote_project_dir):
#                 with prefix(remote_prefix):
#                     run(command)
#         else:
#             run(command)

# env.run_in = smart_run


# @task
# def run_local():
#     env.place = "local"


# @task
# def reset():
#     """
#     Reset local debug env.
#     """

#     env.run_in("""
#     rm -rf /tmp/instance
#     mkdir /tmp/instance
#     """)


# @task
# def setup():
#     """
#     Setup virtual env.
#     """

#     env.run_in("virtualenv env")
#     activate_this = "env/bin/activate_this.py"
#     execfile(activate_this, dict(__file__=activate_this))
#     env.run_in("python setup.py install")
#     reset()


# @task
# def deploy():
#     """
#     Deploy project to Gastos Abertos server
#     """

#     env.run_in("""
#     git pull
#     python setup.py develop
#     touch wsgi.py
#     """, inside_env=True)


# @task
# def initdb():
#     """
#     Init or reset database
#     """

#     env.run_in("python manage.py initdb", inside_env=True)


# @task
# def importdata(lines_per_insert=100):
#     """
#     Import data to the local DB
#     """

#     # env.run_in("""
#     # python utils/import_revenue_codes.py
#     # python utils/import_revenue.py data/receitas_min.csv {lines_per_insert}
#     # python utils/import_contrato.py
#     # """.format(lines_per_insert=lines_per_insert), inside_env=True)
#     env.run_in("python manage.py importdata", inside_env=True)


# @task
# def generate_jsons(year=''):
#     """
#     Generate Jsons for Highcharts
#     """
#     env.run_in("""
#     python utils/generate_total_json.py -o data/total_by_year_by_code {year}
#     """.format(year=year), inside_env=True)


# @task
# def d():
#     """
#     Debug.
#     """

#     reset()
#     local("python manage.py run")


# @task
# def babel():
#     """
#     Babel compile.
#     """

#     env.run_in("python setup.py compile_catalog --directory `find -name translations` -f")


# ----------------------------------------------------
#  OpenShift
# ----------------------------------------------------


# Should be a file with only: {app username} {app name} {namespace}
# Like:
# co2d398k9823792381ko82 my-nice-app my-os-namespace
env.user, env.app, env.ns = open('os_user_and_app.conf',
                                 'r').read().strip().split()
env.hosts = ['{app}-{ns}.rhcloud.com'.format(app=env.app, ns=env.ns)]


def _annotate_hosts_with_ssh_config_info():
    '''
    Parse .ssh/config to get correct keys (avoids "Too many authentication
    failures"). env.hosts must be set.
    http://markpasc.typepad.com/blog/2010/04/loading-ssh-config-settings-for-fabric.html
    '''

    from os.path import expanduser
    from paramiko.config import SSHConfig

    def hostinfo(host, config):
        hive = config.lookup(host)
        if 'hostname' in hive:
            host = hive['hostname']
        if 'user' in hive:
            host = '%s@%s' % (hive['user'], host)
        if 'port' in hive:
            host = '%s:%s' % (host, hive['port'])
        return host

    try:
        config_file = file(expanduser('~/.ssh/config'))
    except IOError:
        pass
    else:
        config = SSHConfig()
        config.parse(config_file)
        keys = [config.lookup(host).get('identityfile', None)
                for host in env.hosts]
        env.key_filename = [expanduser(key[0])
                            for key in keys if key is not None]
        env.hosts = [hostinfo(host, config) for host in env.hosts]

_annotate_hosts_with_ssh_config_info()


def base_os():
    '''Base config for OpenShift.'''

    env.venv = '. $OPENSHIFT_PYTHON_DIR/virtenv/bin/activate'
    env.folder = '~/app-root/repo'
    env.host_type = 'os'
    env.get_settings_folder = lambda: run('echo $OPENSHIFT_DATA_DIR')


def update_settings():
    settings_folder = env.get_settings_folder()

    def put_settings(here, there=None):
        if not there:
            there = here
        with cd(settings_folder):
            # put(os.path.join(env.app, 'settings', here), there)
            put(os.path.join('settings', here), there)

    # put_settings('%s_settings.py' % env.host_type, 'local_settings.py')
    put_settings('os_settings.py', 'production.cfg')


def touch():
    with cd(env.folder):
        run('touch wsgi.py')
