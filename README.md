# splitter
Run test server:
PYTHONPATH=".." DJANGO_SETTINGS_MODULE="settings" python manage.py runserver

PYTHONPATH - path to your config file
DJANGO_SETTINGS_MODULE - name of your config file without ".py"

Install python3
$ sudo apt-get install python3.6 python3.6-dev uwsgi uwsgi-src uuid-dev libcap-dev libpcre3-dev
$ cd ~
$ PYTHON=python3.6 uwsgi --build-plugin "/usr/src/uwsgi/plugins/python python36"
$ sudo mv python36_plugin.so /usr/lib/uwsgi/plugins/python36_plugin.so
$ sudo chmod 644 /usr/lib/uwsgi/plugins/python36_plugin.so
$ uwsgi --plugin python36 -s :0 # Ubuntu 16.10
...
Python version: 3.6.0b2 (default, Oct 11 2016, 05:27:10)  [GCC 6.2.0 20161005]
...
$ uwsgi --plugin python36 -s :0 # Ubuntu 17.04
...
Python version: 3.6.1 (default, Mar 22 2017, 06:17:05)  [GCC 6.3.0 20170321]
...

Install
pip3 install Django
pip3 install psycopg2
pip3 install django-jsonview