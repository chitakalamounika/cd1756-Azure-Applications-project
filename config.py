import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ====== General App Settings ======
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'replace_with_random_secret'

    # ====== Azure Blob Storage ======
    BLOB_ACCOUNT = os.environ.get('BLOB_ACCOUNT') or 'stcd1756mounika'
    BLOB_STORAGE_KEY = os.environ.get('BLOB_STORAGE_KEY')
    BLOB_CONTAINER = os.environ.get('BLOB_CONTAINER') or 'images'

    # ====== Azure SQL Database ======
    SQL_SERVER = os.environ.get('SQL_SERVER') or 'sql-cd1756-moni2.database.windows.net'
    SQL_DATABASE = os.environ.get('SQL_DATABASE') or 'articlecms'
    SQL_USER_NAME = os.environ.get('SQL_USER_NAME') or 'sqladminuser'
    SQL_PASSWORD = os.environ.get('SQL_PASSWORD') or 'Moni1810'
    SQLALCHEMY_DATABASE_URI = (
        'mssql+pyodbc://'
        + SQL_USER_NAME + ':' + SQL_PASSWORD
        + '@' + SQL_SERVER + ':1433/' + SQL_DATABASE
        + '?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ====== Microsoft Authentication ======
    CLIENT_ID = os.environ.get('CLIENT_ID') or 'b56de121-32de-4130-987b-4364998b3ffa'
    TENANT_ID = os.environ.get('TENANT_ID') or 'd93d0786-0aad-4792-93ba-6ea04036af73'
    AUTHORITY = os.environ.get('AUTHORITY') or f'https://login.microsoftonline.com/{TENANT_ID}'

    CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
    REDIRECT_PATH = '/getAToken'
    SCOPE = ["User.Read"]

    SESSION_TYPE = "filesystem"
