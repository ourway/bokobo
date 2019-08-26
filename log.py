# import logging
#
# formatter = logging.Formatter(
#     '[%(asctime)s] p%(process)s {%(pathname)s %(filename)s:%(lineno)d} %(levelname)s - %(message)s', '%m-%d %H:%M:%S')
#
# logging.basicConfig(
#     filename='debug.log',
#     format='%(asctime)s,%(msecs)d %(levelname)-8s [%(pathname)s :%(lineno)d - %(funcName)5s()] %(message)s',
#     datefmt='%Y-%m-%d:%H:%M:%S',
#     level=logging.DEBUG)
#
# logger = logging.getLogger(__name__)
#




import os
import logging

log_file = os.environ.get('log_path')
print('log_file : {}'.format(log_file))



logging.basicConfig(
            filename=log_file,
            format='%(asctime)s,%(msecs)d %(levelname)-8s [%(pathname)s :%(lineno)d - %(funcName)5s()] %(message)s ',
            datefmt='%Y-%m-%d:%H:%M:%S',
            level=logging.DEBUG)
c_handler = logging.StreamHandler()


logger = logging.getLogger(__name__)
logger.addHandler(c_handler)


# logging_example.py
#
# import logging
#
# # Create a custom logger
#
# # Create handlers
# c_handler = logging.StreamHandler()
# f_handler = logging.FileHandler(log_file)
# c_handler.setLevel(logging.DEBUG)
# f_handler.setLevel(logging.DEBUG)
#
# # Create formatters and add it to handlers
# c_format = logging.Formatter('%(asctime)s — %(levelname) — %(username)s — (pathname)s :%(lineno)d - %(funcName)s — %(message)s ')
# f_format = logging.Formatter('%(asctime)s — %(levelname) — %(username)s — (pathname)s :%(lineno)d - %(funcName)s — %(message)s ')
# c_handler.setFormatter(c_format)
# f_handler.setFormatter(f_format)
#
# logger = logging.getLogger(__name__)
#
# # Add handlers to the logger
# logger.addHandler(c_handler)
# logger.addHandler(f_handler)
#
#
#
#
#













#
# import logging
# import sys
# from logging.handlers import TimedRotatingFileHandler
#
#
# FORMATTER = logging.Formatter("%(asctime)s — %(levelname) — %(username)s — (pathname)s :%(lineno)d - %(funcName)s — %(message)s - %(extra)s ")
# def get_console_handler():
#    console_handler = logging.StreamHandler(sys.stdout)
#    console_handler.setFormatter(FORMATTER)
#    return console_handler
# def get_file_handler():
#    print("log file: {}".format(log_file))
#    file_handler = TimedRotatingFileHandler(log_file, when='midnight')
#    file_handler.setFormatter(FORMATTER)
#    return file_handler
# def get_logger(logger_name):

#
#     logger = logging.getLogger(logger_name)
#     # logger.setLevel(logging.DEBUG)
#     logger.addHandler(get_console_handler())
#     # logger.addHandler(get_file_handler())
#    # with this pattern, it's rarely necessary to propagate the error up to parent
#     logger.propagate = False
#     return logger
#
# logger  = get_logger(__name__)


class LogMsg:
    START = "function is called -- user is : %s "
    END = "function finished successfully "
    ADDING_ERR = "adding model to database encountered a problem  "
    DATETIME_ADDITION = "date time added to model  "
    DATA_ADDITION = "data added to model : %s "
    DB_ADD = "model added to database : %s  "
    AUTH_CHECKING = "going to check authentication  "
    AUTH_SUCCEED = "authentication is successful  "
    GET_SUCCESS = "getting from database is successful : %s "
    GET_FAILED = "getting from database failed : %s "
    DELETE_SUCCESS = "deleting item is done successfully  "
    DELETE_FAILED = "deleting the item encountered a problem "
    DELETE_REQUEST = "request for deleting item : %s"
    EDIT_REQUST = "editing the item : %s"
    EDIT_SUCCESS = "editing item is done successfully  "
    EDIT_FAILED = "editing the item encountered a problem  "
    MODEL_GETTING = "model_instance getting from database by id : %s "
    MODEL_GETTING_FAILED = "item is not exists in database  "
    MODEL_ALTERED = "item altered successfully : %s "
    GET_ALL_REQUEST = "getting all request from db..."
    NOT_FOUND = "no such item exists : %s"
    COMMIT_FAILED = 'commiting process failed'
    TOKEN_CREATED = 'a new token for user created'
    TOKEN_EXPIRED = 'token is expired'
    TOKEN_DELETED = 'token deleted successfuly'
    TOKEN_INVALID = 'token is invalid'
    ALTERING_AUTHORITY_FAILED = 'user has no admission to alter the item'
    DELETE_PROCESSING = 'going to delete the item from db'
    GATHERING_RELATIVES = 'gathering item reletives to delete them from db'
    DELETE_RELATIVE = 'the reletive {} is going to be delete'
    UPLOAD_NOT_ALLOWED = 'no more uploads supports in edit'
    POST_ALREADY_LIKED = 'user liked the post before'
    USER_XISTS = 'user by this username : %s already exists'
    PARENT_INVALID = 'parent entity doesnt exist'
    CHECK_REDIS_FOR_EXISTANCE = 'checking redis if cell number already ' \
                                'exists...'
    REGISTER_XISTS = 'user has already valid registery code'
    CHECK_USER_EXISTANCE = 'checking user if already exists'
    GENERATING_REGISTERY_CODE = 'generating key for registering process for ' \
                                'cell no : {}'
    SEND_CODE_BY_SMS = 'registery activation_code is going to send for user by SMS'
    SMS_SENT = 'message sent to user by cell no : {}'
    DATA_MISSING = 'required data doesnt exists in data : {}'
    REGISTER_KEY_INVALID = 'your register activation_code is wrong '
    REGISTER_KEY_DOESNT_EXIST = 'the activation_code expired or doesnt exist '
    USR_ADDING = 'user is going to create...'
    USER_BY_CELL_EXIST = 'user with this cell no already exist'
    NOT_UNIQUE = 'must be unique,change it please'
    NOT_ACCESSED ='this user can not access to this section'
    SCROLL_UNDEFINED = 'scrolling mood is undefined.it should be up or down'
    SCHEMA_CHECKED = 'schema checked for required data'
    USERNAME_NOT_UNIQUE = 'this username already exists'
    TOKEN_KEY_DOESNT_EXIST = 'the token is expired or doesnt exists'
    PERSON_EXISTS = 'person by this username : %s exists'
    NOT_RIGTH_ENTITY_PASSED = 'your entity type is not {}'
    PERSON_NOT_EXISTS = 'person for this username not exists : %s '
    NOT_EDITABLE = 'field is not editable'
    ENTITY_DELETED = 'the entity deleted successfully : %s'
    RELATED_USER_DELETE = 'related user_id of person is {} is going to delete'
    USER_HAS_SIGNUP_TOKEN = 'user has sign up token and new code cant send'
    USER_HAS_ACTIVATION_CODE = 'user already has valid activation code and cant resend code now'
    ENUM_CHECK = 'checking enums to be right type  -  %s'
    USER_CHECKING = 'checking user by username :  %s'
    INVALID_USER = 'user by this username doesnt exist : %s'
    POPULATING_BASIC_DATA = 'new model is populating with basic data'
    EDITING_BASIC_DATA = 'editing basic data for model : %s'

    #Account
    GETTING_USER_ACCOUNTS = 'getting acount of user by type  : %s '
    ACCOUNT_BY_TYPE_EXISTS = 'user has already an account of type : %s '
    GETTING_PERSON_ALL_ACCOUNTS = 'getting all acounts of person_id : %s'
    DELETE_USER_ALL_ACCOUNTS = 'deleting users all accounts username is : %s '
    DELETE_ACCOUNT_BY_ID = 'deleting account by id = %s '
    GETTING_ACCOUNT_BY_ID = 'getting account by id = %s '
    EDIT_ACCOUNT_VALUE = 'changing account value : %s '
    ACCOUNT_VALUE_EDITED = 'the value if account : %s changed successfully'
    ACCOUNT_BY_ID_IS_NOT_FOR_PERSON = 'the account doesnt exist or not owned by user : %s '
    ADD_INITIAL_ACCOUNT = 'adding initial account of type Main for person_id : %s '
    GETTING_ACCOUNT_PERSON = 'getting account by data : %s'
    USER_HAS_NO_ACCOUNT = 'user has no account of type: %s'


    # Token
    CHECKING_VALID_TOKEN = 'checking if user: %s has valid token '
    USER_HAS_VALID_TOKEN = 'user already has valid token : %s '


    # BOOK
    ADD_BOOK = 'adding book by data : %s '
    DELETE_BOOK_FILES = 'deleting files of book by id : %s'
    DELETE_BOOK_IMAGES = 'deleting images of book by id : %s '
    EDITING_BOOK = 'editing book : %s '
    DELETING_BOOK  = 'deleting book by id : %s '
    GETTING_ALL_BOOKS = 'request for getting all books'
    ADDING_MULTIPLE_BOOKS = 'adding multiple books by data : %s '
    ADDING_ROLES_TO_BOOK = 'adding roles to book : %s '
    ATTACHING_ROLES_TO_BOOKS = 'attaching book roles to book entities'
    DELETING_BOOK_ROLES = 'deleting roles of book by id : %s '
    DELETING_BOOK_COMMENTS = 'deleting comments of book : %s '
    DELETING_BOOK_PRICE = 'deleting price of book : %s '
    SEARCH_BOOK_BY_TITLE = 'searching books by titles like : %s '
    SEARCH_BOOK_BY_GENRE = 'searching books by genre like : %s '
    SEARCH_BOOK_BY_PHRASE = 'searching for books by phrase : %s '
    SEARCH_BOOK_BY_TAGS = 'searching for books by tag : %s '
    SEARCH_BOOKS = 'searching for books by filter : %s'
    GETTING_BOOKS_FROM_LIST = 'getting books from list id ids : %s'
    GETTING_NEWEST_BOOKS = 'getting newest book list'
    RESULT_BOOKS = 'result of books is : %s'

    # BOOK_ROLE
    ADDING_ROLES_OF_BOOK = 'adding roles of a book to DB by list : %s'
    ROLE_ADDED = 'role added to book : %s'
    DELETE_BOOK_ROLES = 'deleting all roles for book : %s '
    GET_PERSONS_BOOKS = 'getting all books which person has a role in . the person is : %s'
    PERSON_BOOK_LIST = 'persons list of books which has a role in is : %s '
    GETTING_ROLES_OF_BOOK = 'getting all roles of book : %s'
    BOOKS_ROLES = 'the roles of book is : %s'

    # COMMENT
    COMMENT_VALIDATING_BOOK = 'getting book to validate commenting : %s'
    COMMENT_CHECK_FOR_PARENT = 'checking if comment has a parent'
    COMMENT_GETTING_PARENT = 'getting comment parent by id : %s'
    COMMENT_PARENT_NOT_FOUND = 'comments parent by this id not found : %s'
    COMMENT_PARENT_NOT_MATCH = 'this parent comment is not matching for this book id : %s'
    COMMENT_DELETING_BOOK_COMMENTS = 'deleting all comments of book by id : %s '
    COMMENT_GETTING_BOOK_COMMENTS = 'getting all comments of book by id :%s '

    # COMMENT_ACTION

    ACTION_CHECK_COMMENT = 'checking for comment existance by id : %s'
    ACTION_REPORT_COMMENT = 'reporting comment by id : %s '
    ACTION_DISREPORT_COMMENT = 'disreporting comment by id : %s '
    ACTION_LIKE_COMMENT = 'liking comment by id : %s'
    ACTION_DISLIKE_COMMENT = 'disliking comment by id : %s '
    ACTION_GETTING_LIKES = 'getting comment likes by id : %s'
    ACTION_GETTING_REPORTS = 'getting comment reports by id : %s '
    ACTION_CHECK_USER_LIKED = 'checking if user liked comment already : %s'
    ACTION_CHECK_USER_REPORTED = 'checking if user reported the comment : %s '
    ACTION_ALREADY_LIKED = 'user already liked the comment '
    ACTION_ALREADY_REPORTED = 'user already reported the comment'
    ACTION_USER_CANT_DISLIKE = 'user not liked the comment so cant dislike it'
    ACTION_USER_CANT_DISREPORT = 'user not reported the comment so cant desreport it'


    # Price
    ADDING_PRICE = 'adding price for book : %s '
    CHECK_BOOK_PRICE_EXISTANCE = 'checking if book already has price in db : %s'
    BOOK_PRICE_EXISTS = 'book by this id already has price: %s'
    EDIT_PRICE = 'editing book price by id : %s'
    ADD_NEW_BOOK_PRICE = 'adding new price entity for book : %s'

    # Elasticsearch
    INDEXING_IN_ELASTIC = 'indexing book data in elastic search : %s '
    ELASTIC_INDEX_DELETE = 'deleting book index in elastic search by id : %s'
    SEARCH_ELASTIC_INDEXES = 'searching in elastic search for indexes by phrase : %s '
    ELASTIC_SEARCH_RESULTS = 'elastic search result for book_id s is : %s '



    # USER
    USER_HAS_NO_PERSON = 'user by ths username has no related person : %s '
    NOT_RELATED_USER_FOR_PERSON = 'person has not related user : %s'


    # PERSON
    PERSON_HAS_BOOKS = 'person already has roles for books '


    # UNIQUE CONSTRAINT
    GENERATE_UNIQUE_CONSTRAINT = 'generating unique constraint key for book by data : %s'
    CHECK_UNIQUE_EXISTANCE = 'checking for existance of unique code : %s'
    UNIQUE_CONSTRAINT_EXISTS = 'the unique costraint key already exists : %s'





    UPLOAD_FAILED = 'uploading files failed'
    FILE_EXISTS = 'this file exists by path : %s'
    FILE_NOT_EXISTS = 'file by this path not exists: %s'
    GET_FILE_FAILED = 'file can not be got'

    COMMIT_ERROR = 'commiting to db encountered problem'