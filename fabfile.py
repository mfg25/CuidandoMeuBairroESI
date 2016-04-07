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

local_old_data_folder = '../gastos_abertos_dados/Orcamento/execucao/'

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
    put_settings('custom_os_settings.py', 'production.cfg')
    try:
        put_settings('transfer.conf')
    except:
        pass


def touch():
    with cd(env.folder):
        run('touch wsgi.py')


def upload_old_data():
    '''
    The CSVs must already be processed localy.
    '''
    settings_folder = env.get_settings_folder()
    old_data_folder = os.path.join(settings_folder, 'old_data')
    run('mkdir ' + old_data_folder)

    local_files = [x for x in os.listdir(local_old_data_folder)
                   if x.endswith('.csv')]

    with cd(old_data_folder):
        for f in local_files:
            put(os.path.join(local_old_data_folder, f), f)


def upload_geo_cache():
    settings_folder = env.get_settings_folder()
    cache_folder = os.path.join(settings_folder, 'geo_cache')
    try:
        run('mkdir ' + cache_folder)
    except:
        pass
    geo_data_folder = 'utils/geocoder/data/'
    with cd(cache_folder):
        f = 'cache.db'
        put(os.path.join(geo_data_folder, f), f)
        f = 'subprefeituras.geojson'
        put(os.path.join(geo_data_folder, f), f)


def upload_ga_dados_code():
    '''
    This code is used as requirement for the daily update script.
    '''
    settings_folder = env.get_settings_folder()
    ga_dados_folder = os.path.join(settings_folder, 'ga_dados')
    try:
        run('mkdir ' + ga_dados_folder)
    except:
        pass
    try:
        run('mkdir ' + os.path.join(ga_dados_folder, 'store'))
    except:
        pass
    try:
        run('mkdir ' + os.path.join(ga_dados_folder, 'public'))
    except:
        pass
    local_ga_dados_folder = '../gastos_abertos_dados/utils'
    with cd(ga_dados_folder):
        f = 'execucao_downloader.py'
        put(os.path.join(local_ga_dados_folder, f), f)
        f = 'requirements.txt'
        put(os.path.join(local_ga_dados_folder, f), f)
        run('pip install -r %s' % f)


def initdb():
    with cd(env.folder):
        run("python manage.py -i %s initdb" % env.get_settings_folder())


def importdata(reset=False):
    c = 'python manage.py -i {inst} importdata -d execucao'
    if reset:
        c += ' -r'
    c += ' -e {data} -g {cache}'
    sf = env.get_settings_folder()
    with cd(env.folder):
        run(c.format(inst=sf,
                     data=os.path.join(sf, 'old_data'),
                     cache=os.path.join(sf, 'geo_cache')))
