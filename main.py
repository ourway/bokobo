from bottle import Bottle, run

from register.urls import call_router as register_routes
from user.urls import call_router as user_routes
from sign_up.urls import call_router as signup_routes
from app_token.urls import call_router as token_routes
from books.urls import call_router as book_routes
from file_handler.urls import call_router as file_routes
from comment.urls import call_router as comment_routes
from follow.urls import call_router as follow_routes
from book_rate.urls import call_router as rate_routes
from wish_list.urls import call_router as wish_routes
from book_collections.urls import call_router as collection_routes
from accounts.urls import call_router as account_routes
from financial_transactions.urls import call_router as transaction_routes
from prices.urls import call_router as price_routes
from order.urls import call_router as order_routes

app = Bottle()

user_routes(app)
register_routes(app)
signup_routes(app)
token_routes(app)
book_routes(app)
file_routes(app)
comment_routes(app)
follow_routes(app)
rate_routes(app)
wish_routes(app)
collection_routes(app)
account_routes(app)
transaction_routes(app)
price_routes(app)
order_routes(app)



if __name__ == '__main__':
    print('hello world')


    run(host='0.0.0.0', port=7000, debug=True, app=app)

