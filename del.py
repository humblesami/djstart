import os
import glob
from pathlib import Path


def remove_migrations():
    res = glob.glob('*/migrations/*', recursive=True)
    for file_path in res:
        if file_path.endswith('__pycache__'):
            file_path = file_path+'/*'
            sub_res = glob.glob(file_path)
            for file_path in sub_res:
                os.remove(file_path)
        elif not file_path.endswith('__init__.py'):
            os.remove(file_path)
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
    print('Migration files removed')


def remove_file_by_extension(ext):
    cnt = 0
    dir_path = os.path.dirname(os.path.realpath(__file__))
    files = Path(dir_path).rglob('*.'+ext)
    for path in files:
        os.remove(str(path))
        cnt += 1
    print(str(cnt) + ' ' + ext + ' files removed')


remove_migrations()
remove_file_by_extension('pyc')
remove_file_by_extension('po')
print('done')

