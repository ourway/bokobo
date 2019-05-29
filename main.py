from bottle import Bottle, run

from db_session import recreate_database

if __name__ == '__main__':
    print('hello world')

    app = Bottle()

    run(host='localhost', port=7000, debug=True, app=app)

