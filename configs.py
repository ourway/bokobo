import enum

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

class Roles(enum.Enum):
    Author = 'author'
    Writer = 'writer'
    Translator = 'translator'
    Press = 'press'
    Contributer = 'contributer'
    Designer = 'designer'


class BookTypes(enum.Enum):
    DVD = 'dvd'
    Audio = 'audio'
    Hard_Copy = 'hard_copy'
    Pdf = 'pdf'
    Epub = 'epub'

class Genre(enum.Enum):
    Comedy = 'comedy'
    Drama = 'drama'
    Romance = 'romance'
    Social = 'social'
    Religious = 'religious'
    Historical = 'historical'


DATABASE_URI = 'postgres+psycopg2://{}:{}@{}:{}/{}'.format(Database.db_user, Database.db_pass,
                                                                                Database.db_host, Database.db_port,
                                                                                Database.db_name)
CELERY_DATABASE_URI = 'db+postgresql+psycopg2://{}:{}@{}:{}/{}'.format(CeleryConfigs.db_user, CeleryConfigs.db_pass,
                                                                                CeleryConfigs.db_host, CeleryConfigs.db_port,
                                                                                CeleryConfigs.db_name)

ADMINISTRATORS = ['admin']
SIGNUP_USER = 'signup_user'

