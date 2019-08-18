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
    DATA_ADDITION = "data added to model  "
    DB_ADD = "model added to database : %s  "
    AUTH_CHECKING = "going to check authentication  "
    AUTH_SUCCEED = "authentication is successful  "
    GET_SUCCESS = "getting from database is successful : %s "
    GET_FAILED = "getting from database failed : %s "
    DELETE_SUCCESS = "deleting item is done successfully  "
    DELETE_FAILED = "deleting the item encountered a problem  "
    DELETE_REQUEST = "request for deleting item..."
    EDIT_REQUST = "editing the item..."
    EDIT_SUCCESS = "editing item is done successfully  "
    EDIT_FAILED = "editing the item encountered a problem  "
    MODEL_GETTING = "model_instance got from database successfully  "
    MODEL_GETTING_FAILED = "item is not exists in database  "
    MODEL_ALTERED = "item altered successfully  "
    GET_ALL_REQUEST = "getting all request from db..."
    NOT_FOUND = "no such item exists "
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
    ENTITY_DELETED = 'the entity deleted successfully'
    RELATED_USER_DELETE = 'related user_id of person is {} is going to delete'
    USER_HAS_SIGNUP_TOKEN = 'user has sign up token and new code cant send'
    USER_HAS_ACTIVATION_CODE = 'user already has valid activation code and cant resend code now'
    ENUM_CHECK = 'checking enums to be right type  -  %s'
    USER_CHECKING = 'checking user by username :  %s'
    INVALID_USER = 'user by this username doesnt exist : %s'
    POPULATING_BASIC_DATA = 'new model is populating with basic data'

    #Account
    GETTING_USER_ACCOUNTS = 'getting acount of user by type  : %s '
    ACCOUNT_BY_TYPE_EXISTS = 'user has already an account of type : %s '
    GETTING_PERSON_ALL_ACCOUNTS = 'getting all acounts of person_id : %s'
    DELETE_USER_ALL_ACCOUNTS = 'deleting users all accounts username is : %s '
    DELETE_ACCOUNT_BY_ID = 'deleting account by id = %s '
    GETTING_ACCOUNT_BY_ID = 'getting account by id = %s '
    EDIT_ACCOUNT_VALUE = 'changing account value : %s '
