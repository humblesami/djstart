import os
import sys
import uuid
import asyncio
import requests
import threading
import traceback
from pathlib import Path
from os.path import dirname
from django.apps import apps
from django.conf import settings
from django.db import connection
from datetime import datetime, timezone


dir_path = str(settings.BASE_DIR)
try:
    os.makedirs(dir_path + '/logs')
except:
    pass


class Exceptions:

    @classmethod
    def get_error_message(cls):
        eg = traceback.format_exception(*sys.exc_info())
        error_message = ''
        cnt = 0
        for er in eg:
            cnt += 1
            if not 'lib/python' in er and not 'lib\site-packages' in er:
                error_message += " " + er
        return error_message

    @classmethod
    def get_error_json(cls):
        eg = traceback.format_exception(*sys.exc_info())
        user = eg[len(eg) - 1]
        dev = cls.get_error_message()
        return {'user': user, 'dev': dev}


class Logs:

    @classmethod
    def write_file(cls, content='Nothing', file_name=''):
        if not file_name:
            file_name = dir_path + '/logs/errors.log'
        else:
            file_name = dir_path + '/logs/' + file_name
        f = open(file_name, "a+")
        file_data = f.read() or ''
        time_now = '' + str(datetime.now())
        content = file_data + '\n' + content + '--' + time_now
        f.write(content)
        f.close()

    @classmethod
    def prepend(cls, file_path, txt, take_lines=20):
        dt_now = str(datetime.now(tz=timezone.utc))[:19]
        fle = Path(file_path)
        fle.touch(exist_ok=True)
        with open(file_path, 'r') as my_file:
            i = 0
            prev_content = ''
            while i < take_lines:
                try:
                    line = next(my_file)
                    prev_content += '\n' + line.strip()
                except:
                    break
                i += 1
        with open(file_path, 'w') as my_file:
            new_content = dt_now + '\t' + txt + prev_content
            my_file.write(new_content)


class Async:
    def background(cls, bg_fun):
        def wrapped(*args, **kwargs):
            looper = None
            try:
                looper = asyncio.get_event_loop()
            except RuntimeError as ex:
                if "There is no current event loop in thread" in str(ex):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    looper = asyncio.get_event_loop()
            return looper.run_in_executor(None, bg_fun, *args)

        return wrapped

    @classmethod
    async def async_functions_list_processor(cls, tasks_list):
        coroutines = []
        for task_to_do in tasks_list:
            coroutines.append(task_to_do)
        res = await asyncio.gather(*coroutines)
        return res

    @classmethod
    def threaded_operation(cls, operation, args):
        obj = threading.Thread(target=operation, args=args)
        obj.start()


class DateTime:
    @classmethod
    def time_to_utc(cls, dt):
        # dst_str = str(dt)
        # dst_str = '2021-09-21T09:29:21Z'
        dt_str = str(dt)
        dt_str = dt_str.replace(' ', 'T')
        if '.' in dt_str:
            dt_str = dt_str[:19] + 'Z'
        else:
            dt_str = dt_str.replace('+00:00', 'Z')
        return dt_str

    @classmethod
    def get_month_year(cls, dt):
        year = str(dt.year)
        month = dt.month
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        return year, month


class Http:
    @classmethod
    def get_client_ip(cls, req_meta):
        x_forwarded_for = req_meta.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = req_meta.get('REMOTE_ADDR')
        return ip

    @classmethod
    def http_get(cls, req_url, timeout=5):
        res = requests.get(req_url, timeout=timeout)
        return res

    @classmethod
    def http_request(cls, req_url, headers=None):
        try:
            if headers:
                res = requests.get(req_url, headers=headers)
            else:
                res = requests.get(req_url)
            res = res._content.decode("utf-8")
            return res
        except:
            res = Exceptions.get_error_message()
            return res

    @classmethod
    def http_post(cls, req_url, args=None, timeout=6):
        try:
            json_data = args.get('json')
            headers = args.get('headers') # 'application/json' if json_data else None
            res = requests.post(req_url, timeout=timeout, json=json_data, headers=headers)
            res = res._content.decode("utf-8")
            return res
        except:
            res = Exceptions.get_error_message()
            return res


class Python:

    @classmethod
    def unique_id(cls):
        res = str(uuid.uuid4())
        return res


class Db:
    @classmethod
    def execute_update(cls, query, params=None):
        cr = connection.cursor()
        if params:
            cr.execute(query, params)
        else:
            cr.execute(query)
        res = cr.rowcount
        return res

    @classmethod
    def execute_query(cls, query, params=None):
        cr = connection.cursor()
        if params:
            cr.execute(query, params)
        else:
            cr.execute(query)
        rows = cr.fetchall()
        return rows

    @classmethod
    def dict_fetch_all(cls, query, params=None):
        cr = connection.cursor()
        if params:
            cr.execute(query, params)
        else:
            cr.execute(query)
        desc = cr.description
        res = [dict(zip([col[0].replace('.', '=>') for col in desc], row)) for row in cr.fetchall()]
        return res

    @classmethod
    def get_fields_for_tables(cls, tables):
        table_names = "','".join(tables)
        db_name = connection.settings_dict['NAME']
        query = "select concat(table_name,'.',column_name) from information_schema.columns"
        query += f" where table_schema='{db_name}' and table_name in ('{table_names}')"
        res = cls.execute_query(query)
        columns = []
        for item in res:
            columns.append(item[0])
        return columns


class Django:
    @classmethod
    def get_django_model(cls, app_name, model_name):
        try:
            model = apps.get_model(app_name, model_name)
            return model
        except:
            return 'model not found'
