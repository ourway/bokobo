class Database:
    db_user ='libuser'
    db_pass = 'libpass'
    db_host = 'localhost'
    db_port = '5432'
    db_name = 'online_library'


DATABASE_URI = 'postgres+psycopg2://{}:{}@{}:{}/{}'.format(Database.db_user, Database.db_pass,
                                                                                Database.db_host, Database.db_port,
                                                                                Database.db_name)
