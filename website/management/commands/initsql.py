import os
import sys
import importlib
import traceback
from os.path import dirname
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'setting up db i.e. create db or drop db for dev purpose'
    settings_dir = dirname(__file__)

    def drop_create_db(self):
        module_path = dirname(dirname(dirname(__file__)))
        root_path = dirname(module_path)

        database_info = {}
        database_info = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': root_path + '/db.sqlite3',
        }

        db_engine = database_info['ENGINE']
        if db_engine.endswith('sqlite3'):
            db_path = root_path + '/db.sqlite3'
            if os.path.exists(db_path):
                os.remove(db_path)
        call_command('makemigrations')
        call_command('migrate')
        fixture_path = module_path + '/fixtures/init.json'

        if os.path.isfile(fixture_path):
            call_command('loaddata', fixture_path)
        importlib.import_module('del')
        return 'created'

    def add_arguments(self, parser):
        parser.add_argument('-hard', '--hard', action='store_true', help='drop database if exists and create new one')

    def handle(self, *args, **kwargs):
        try:
            self.drop_create_db()
            print('Created successfully')
        except:
            eg = traceback.format_exception(*sys.exc_info())
            error_message = ''
            cnt = 0
            for er in eg:
                cnt += 1
                if not 'lib/python' in er and not 'lib\site-packages' in er:
                    error_message += " " + er
            print('Error ' + error_message)
