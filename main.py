from bottle import Bottle, run

from register.urls import call_router as register_rputes
from user.urls import call_router as user_routes

if __name__ == '__main__':
    print('hello world')

    app = Bottle()


    user_routes(app)
    register_rputes(app)

    run(host='localhost', port=7000, debug=True, app=app)

