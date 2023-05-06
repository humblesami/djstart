import os
import sys
import json
import shutil
import importlib
import traceback
from MySQLdb import connect
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'setting up db i.e. create db or drop db for dev purpose'
    settings_dir = os.path.dirname(__file__)
    str = 'website/management/commands'
    base_directory = ''
    if str in settings_dir:
        base_directory = settings_dir.replace(str, '')
    else:
        str = 'website\\management\\commands'
        base_directory = settings_dir.replace(str, '')

    @classmethod
    def make_copy_database(cls, old_db, new_db, tables, cur, db_con):
        sql_query = 'drop database if exists ' + new_db
        cur.execute(sql_query)

        # cur.execute("SET GLOBAL default_storage_engine = 'InnoDB'")
        sql_query = 'create database ' + new_db
        sql_query += " DEFAULT CHARACTER set utf8mb4 collate utf8mb4_unicode_ci"
        cur.execute(sql_query)
        importlib.import_module('del')
        call_command('makemigrations')
        call_command('migrate')

        print('\nNow copying data\n')

        def copy_table(x):
            cols = cls.get_matching_columns(cur, old_db, new_db, x[0])
            cols_str = ",".join(cols)
            sql = f"INSERT INTO {new_db}.{x[0]}({cols_str}) SELECT {cols_str} from {old_db}.{x[0]}"
            cur.execute(sql)
            try:
                cur.execute(sql)
                print('Copied simply Table ' + x[0])
            except Exception as ex:
                try:
                    ex_str = str(ex)
                    if 'Duplicate entry' in ex_str:
                        print('Ignored Table ' + x[0] + ' for duplicates')
                    else:
                        print('Error in query\n')
                        print(f'{sql}\n')
                        print(f'{ex_str}\n')
                except Exception as ex1:
                    ex_str = str(ex1)
                    print(ex_str)
                    raise ex1

        [copy_table(x) for x in tables]
        cur.close()
        db_con.commit()
        return 'copied'

    def get_conn_info(self):
        config_path = f'{self.base_directory}config.json'
        database_info = "No config found"
        config_path = config_path.format(self.base_directory)
        if not os.path.exists(config_path):
            example_config_path = f'{self.base_directory}install/example.config.json'
            if not os.path.exists(example_config_path):
                return 'no config exists'
            shutil.copyfile(example_config_path, config_path)

        config_info = False
        with open(config_path, 'r') as config:
            config_info = json.load(config)

        if config_info:
            active_db = config_info.get('active_conn')
            if active_db:
                db_config = config_info.get(active_db)
                if db_config:
                    database_info = config_info[active_db]
        if not database_info:
            return 'No db info given in config'
        old_db = config_info.get('source_db')
        return database_info, old_db

    def copy_db_data(self):
        database_info, old_db = self.get_conn_info()
        new_db = database_info['NAME']
        db_con = connect(host="localhost", user=database_info['USER'], passwd=database_info['PASSWORD'])
        cur = db_con.cursor()
        sql_query = f"select table_name from information_schema.tables WHERE table_rows>0 and TABLE_SCHEMA='{old_db}'"
        sql_query += " and table_name not in ('django_migrations') order by table_rows"
        cur.execute(sql_query)
        tables = cur.fetchall()
        self.__class__.make_copy_database(old_db, new_db, tables, cur, db_con)
        return 'copied'

    def add_arguments(self, parser):
        parser.add_argument('-hard', '--hard', help='Hard')

    @classmethod
    def get_matching_columns(cls, cur, db1, db2, table_name):
        query = f"select column_name from information_schema.columns where table_schema='{db1}'"
        query += f" and table_name='{table_name}' order by table_name"
        cur.execute(query)
        rows1 = cur.fetchall()
        data1 = [x[0] for x in rows1]
        query = query.replace(f"'{db1}'", f"'{db2}'")
        cur.execute(query)
        rows2 = cur.fetchall()
        data2 = [x[0] for x in rows2]
        matches = set(data1).intersection(data2)
        return matches

    def test1(self):
        database_info, old_db = self.get_conn_info()
        new_db = database_info['NAME']
        db_con = connect(host="localhost", user=database_info['USER'], passwd=database_info['PASSWORD'])
        cur = db_con.cursor()
        return self.get_matching_columns(cur, old_db, new_db, 'pages')

    def handle(self, *args, **kwargs):
        try:
            res = self.copy_db_data()
            # res = self.test1()
            print('Result ' + str(res))
        except:
            eg = traceback.format_exception(*sys.exc_info())
            error_message = ''
            cnt = 0
            for er in eg:
                cnt += 1
                if not 'lib/python' in er and not 'lib\site-packages' in er:
                    error_message += " " + er
            print('Error ' + error_message)
