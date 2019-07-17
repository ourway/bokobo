from bottle import Bottle, run

from register.urls import call_router as register_routes
from user.urls import call_router as user_routes
from sign_up.urls import call_router as signup_routes
from app_token.urls import call_router as token_routes
from books.urls import call_router as book_routes
from file_handler.urls import call_router as file_routes
from comment.urls import call_router as comment_routes

app = Bottle()

user_routes(app)
register_routes(app)
signup_routes(app)
token_routes(app)
book_routes(app)
file_routes(app)
comment_routes(app)

if __name__ == '__main__':
    print('hello world')


    run(host='0.0.0.0', port=7000, debug=True, app=app)

