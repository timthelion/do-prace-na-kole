"""

This fabric file makes setting up and deploying a django application much
easier, but it does make a few assumptions. Namely that you're using Git,
Apache and mod_wsgi and your using Debian or Ubuntu. Also you should have 
Django installed on your local machine and SSH installed on both the local
machine and any servers you want to deploy to.

_note that I've used the name project_name throughout this example. Replace
this with whatever your project is called._

First step is to create your project locally:

    mkdir project_name
    cd project_name
    django-admin.py startproject project_name

Now add a requirements file so pip knows to install Django. You'll probably
add other required modules in here later. Creat a file called requirements.txt
and save it at the top level with the following contents:

    Django
    
Then save this fabfile.py file in the top level directory which should give you:
    
    project_name
        fabfile.py
        requirements.txt
        project_name
            __init__.py
            manage.py
            settings.py
            urls.py

You'll need a WSGI file called project_name.wsgi, where project_name 
is the name you gave to your django project. It will probably look 
like the following, depending on your specific paths and the location
of your settings module

    import os
    import sys

    # put the Django project on sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

    os.environ["DJANGO_SETTINGS_MODULE"] = "project_name.settings"

    from django.core.handlers.wsgi import WSGIHandler
    application = WSGIHandler()

Last but not least you'll want a virtualhost file for apache which looks 
something like the following. Save this as project_name in the inner directory.
You'll want to change /path/to/project_name/ to the location on the remote
server you intent to deploy to.

    <VirtualHost *:80>
        WSGIDaemonProcess project_name-production user=project_name group=project_name threads=10 python-path=/path/to/project_name/lib/python2.6/site-packages
        WSGIProcessGroup project_name-production

        WSGIScriptAlias / /path/to/project_name/releases/current/project_name/project_name.wsgi
        <Directory /path/to/project_name/releases/current/project_name>
            Order deny,allow
            Allow from all
        </Directory>

        ErrorLog /var/log/apache2/error.log
        LogLevel warn

        CustomLog /var/log/apache2/access.log combined
    </VirtualHost>

Now create a file called .gitignore, containing the following. This
prevents the compiled python code being included in the repository and
the archive we use for deployment.

    *.pyc

You should now be ready to initialise a git repository in the top
level project_name directory.

    git init
    git add .gitignore project_name
    git commit -m "Initial commit"

All of that should leave you with 
    
    project_name
        .git
        .gitignore
        requirements.txt
        fabfile.py
        project_name
            __init__.py
            project_name
            project_name.wsgi
            manage.py
            settings.py
            urls.py

In reality you might prefer to keep your wsgi files and virtual host files
elsewhere. The fabfile has a variable (config.virtualhost_path) for this case. 
You'll also want to set the hosts that you intend to deploy to (config.hosts)
as well as the user (config.user).

The first task we're interested in is called setup. It installs all the 
required software on the remote machine, then deploys your code and restarts
the webserver.

    fab local setup

After you've made a few changes and commit them to the master Git branch you 
can run to deply the changes.
    
    fab local deploy

If something is wrong then you can rollback to the previous version.

    fab local rollback
    
Note that this only allows you to rollback to the release immediately before
the latest one. If you want to pick a arbitrary release then you can use the
following, where 20090727170527 is a timestamp for an existing release.

    fab local deploy_version:20090727170527

If you want to ensure your tests run before you make a deployment then you can 
do the following.

    fab local test deploy

"""
from fabric.state import env
from fabric.api import abort, cd, env, get, hide, hosts, prompt, \
            put, require, roles, run, runs_once, settings, show, sudo, warn
from fabric import api

# globals

env.project_name = 'dpnk'

# environments

def local():
    "Use the local virtual server"
    env.hosts = ['127.0.0.1']
    env.path = '/home/petr/soubory/programovani/Auto-mat/DPNK/dpnk-fabric-deploy'
    env.user = 'petr'
    env.virtualhost_path = "/"

def dpnk_test():
    "Use the local virtual server"
    env.hosts = ['auto-mat.cz']
    env.path = '/home/aplikace/dpnk-devel'
    env.user = 'pdlouhy'
    env.virtualhost_path = "/"

def dpnk():
    "Use the local virtual server"
    env.hosts = ['auto-mat.cz']
    env.path = '/home/aplikace/dpnk-new'
    env.user = 'pdlouhy'
    env.virtualhost_path = "/"

# tasks

def test():
    "Run the test suite and bail out if it fails"
    api.local("python manage.py test" % env)

def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories, then run
    a full deployment
    """
    require('hosts', provided_by=[local])
    require('path')
    
    sudo('apt-get install python-setuptools apache2 libapache2-mod-wsgi')
    sudo('easy_install pip')
    sudo('pip install virtualenv')
    # we want rid of the defult apache config
    run('mkdir -p %(path)s; cd %(path)s; virtualenv env --no-site-packages;' % env)
    run('cd %(path)s; mkdir -p releases db_backup static shared packages;' % env)
    deploy()

def deploy():
    """
    Deploy the latest version of the site to the servers, install any
    required third party modules, install the virtual host and 
    then restart the webserver
    """
    require('hosts', provided_by=[local])
    require('path')

    import time
    env.release = api.local("git rev-parse --short HEAD", capture=True)
    #env.release = time.strftime('%Y%m%d%H%M%S')

    upload_tar_from_git()
    install_requirements()
    #install_site()
    symlink_current_release()
    collectstatic()

def deploy_version(version):
    "Specify a specific version to be made live"
    require('hosts', provided_by=[local])
    require('path')
    
    env.version = version
    run('cd %(path)s; rm releases/previous; mv releases/current releases/previous;' % env)
    run('cd %(path)s; ln -s %(version)s releases/current' % env)
    #restart_webserver()

def rollback():
    """
    Limited rollback capability. Simple loads the previously current
    version of the code. Rolling back again will swap between the two.
    """
    require('hosts', provided_by=[local])
    require('path')

    run('cd %(path)s; mv releases/current releases/_previous;' % env)
    run('cd %(path)s; mv releases/previous releases/current;' % env)
    run('cd %(path)s; mv releases/_previous releases/previous;' % env)
    #restart_webserver()
    
# Helpers. These are called by other functions rather than directly

def upload_tar_from_git():
    require('release', provided_by=[deploy, setup])
    "Create an archive from the current Git master branch and upload it"
    api.local('git archive --format=tar HEAD | gzip > %(release)s.tar.gz' % env)
    run('mkdir %(path)s/releases/%(release)s' % env)
    put('%(release)s.tar.gz' % env, '%(path)s/packages/' % env)
    run('cd %(path)s/releases/%(release)s && tar zxf ../../packages/%(release)s.tar.gz' % env)
    run('cd %(path)s/releases/%(release)s/project && ln -s ../../../settings_local.py .' % env)
    run('cd %(path)s/releases/%(release)s && ln -s ../../env .' % env)
    run('cd %(path)s/releases/%(release)s && ln -s ../../db_backup .' % env)
    run('cd %(path)s/releases/%(release)s && ln -s ../../static .' % env)
    api.local('rm %(release)s.tar.gz' % env)

def collectstatic():
    "Collect static files"
    run('cd %(path)s/releases/current/;  env/bin/python manage.py collectstatic --noinput' % env)

def install_site():
    "Add the virtualhost file to apache"
    require('release', provided_by=[deploy, setup])
    sudo('cd %(path)s/releases/%(release)s; cp %(project_name)s%(virtualhost_path)s%(project_name)s /etc/apache2/sites-available/' % env)
    sudo('cd /etc/apache2/sites-available/; a2ensite %(project_name)s' % env) 

def install_requirements():
    "Install the required packages from the requirements file using pip"
    require('release', provided_by=[deploy, setup])
    run('cd %(path)s; env/bin/pip install -r ./releases/%(release)s/requirements.txt' % env)

def symlink_current_release():
    "Symlink our current release"
    require('release', provided_by=[deploy, setup])
    with settings(warn_only=True):
        run('cd %(path)s; rm releases/previous; mv releases/current releases/previous;' % env)
    run('cd %(path)s; ln -s %(release)s releases/current' % env)

def migrate():
    "Update the database"
    dbbackup()
    run('cd %(path)s/releases/current/;  env/bin/python manage.py migrate' % env)

def dbbackup():
    require('release', provided_by=[deploy, setup])
    run('cd %(path)s/releases/current/;  env/bin/python manage.py dbbackup --compress' % env)

def restart_webserver():
    "Restart the web server"
    sudo('/etc/init.d/apache2 restart')