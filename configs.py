

class Database:
    db_user ='libuser'
    db_pass = 'libpass'
    db_host = 'localhost'
    db_port = '5432'
    db_name = 'online_library'

class CeleryConfigs:
    db_user = 'libuser'
    db_pass = 'libpass'
    db_host = 'localhost'
    db_port = '5432'
    db_name = 'celery'


DATABASE_URI = 'postgres+psycopg2://{}:{}@{}:{}/{}'.format(Database.db_user, Database.db_pass,
                                                                                Database.db_host, Database.db_port,
                                                                                Database.db_name)
CELERY_DATABASE_URI = 'db+postgresql+psycopg2://{}:{}@{}:{}/{}'.format(CeleryConfigs.db_user, CeleryConfigs.db_pass,
                                                                                CeleryConfigs.db_host, CeleryConfigs.db_port,
                                                                                CeleryConfigs.db_name)

ADMINISTRATORS = ['admin','kk']
SIGNUP_USER = 'signup_user'
ONLINE_BOOK_TYPES = ['Epub', 'Audio', 'Pdf']


