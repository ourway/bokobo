
import datetime
import logging
from os import environ
import time
from base64 import b64encode, b64decode

import magic
from bottle import request, HTTPResponse

from log import LogMsg
from app_token.models import APP_Token
from user.models import User
from db_session import Session
import json


def model_to_dict(obj):
    object_dict = dict((name, getattr(obj, name)) for name in dir(obj) if
                       not name.startswith('_')) if not isinstance(obj,
                                                                   dict) else obj

    if "metadata" in object_dict:
        del object_dict['metadata']
    print(object_dict)
    return object_dict

def multi_model_to_dict(obj_list):
    result = {}
    for item in obj_list:
        obj = model_to_dict(item)
        result.update(obj)
    return result


def check_auth(func):
    def wrapper(*args, **kwargs):
        logging.debug(LogMsg.AUTH_CHECKING)

        kwargs['username'] = check_Authorization()['username']

        logging.debug(LogMsg.AUTH_SUCCEED)
        logging.debug("user is {}".format(kwargs['username']))

        rtn = func(*args, **kwargs)
        return rtn

    return wrapper

def if_login(func):
    def wrapper(*args, **kwargs):
        logging.debug(LogMsg.AUTH_CHECKING)

        kwargs['username'] = check_login()['username']

        logging.debug(LogMsg.AUTH_SUCCEED)
        logging.debug("user is {}".format(kwargs['username']))

        rtn = func(*args, **kwargs)
        return rtn

    return wrapper

def check_login():
    db_session = get_db_session()
    auth = request.get_header('Authorization')
    if auth is None:
        return {'username':None}

    username, password = decode(auth)
    print(username, password)

    if password is None:
        return model_to_dict(validate_token(username, db_session))

    else:
        user = db_session.query(User).filter(User.username == username,
                                             User.password == password).first()

        if user is None:
            return {'username':None}
        return model_to_dict(user)



def check_Authorization():
    db_session = get_db_session()
    auth = request.get_header('Authorization')
    if auth is None:
        raise Http_error(401, 'no auth found')

    username, password = decode(auth)
    print(username, password)

    if password is None:
        return model_to_dict(validate_token(username, db_session))

    else:
        user = db_session.query(User).filter(User.username == username,
                                             User.password == password).first()

        if user is None:
            raise Http_error(401, {'username':'not valid'})
        return model_to_dict(user)


def encode(username, password):
    """Returns an HTTP basic authentication encrypted string given a valid
    username and password.
    """
    if ':' in username:
        raise Http_error(400, "username has not valid schema")

    username_password = '%s:%s' % (str(username), str(password))
    return 'Basic ' + b64encode(username_password.encode()).decode()


def decode(encoded_str):
    """Decode an encrypted HTTP basic authentication string. Returns a tuple of
    the form (username, password), and raises a DecodeError exception if
    nothing could be decoded.
    """
    split = encoded_str.strip().split(' ')

    # If split is only one element, try to decode the username and password
    # directly.
    if len(split) == 1:
        try:
            username, password = b64decode(split[0]).decode().split(':', 1)
        except:
            raise Http_error(400, "Basic Authentication decoding failed")

    # If there are only two elements, check the first and ensure it says
    # 'basic' so that we know we're about to decode the right thing. If not,
    # bail out.
    elif len(split) == 2:
        if split[0].strip().lower() == 'basic':
            logging.debug("auth is basic")
            try:
                username, password = b64decode(split[1]).decode().split(':', 1)
            except:
                raise Http_error(400, " Authentication decoding failed")

        elif split[0].strip().lower() == 'bearer':
            logging.debug("auth is bearer")
            print(split[0].strip())
            print(split[1].strip())
            username, password = split[1].strip(), None
            logging.debug(
                "token is {} and pass is {}".format(username, password))
        else:
            raise Http_error(400, " Bearer authentication decoding failed")

    # If there are more than 2 elements, something crazy must be happening.
    # Bail.
    else:
        raise Http_error(400, "Basic Authentication decoding failed")

    if password is None:
        return str(username), password

    return str(username), str(password)


def get_db_session():
    if hasattr(request, 'db_session'):
        return request.db_session
    else:
        request.db_session = Session()
        return request.db_session


def inject_db(func):
    def wrapper(*args, **kwargs):
        kwargs['db_session'] = get_db_session()
        rtn = func(*args, **kwargs)
        db_session = kwargs['db_session']
        try:
            db_session.commit()
        except:

            raise Http_error(500, {LogMsg.COMMIT_FAILED:db_session.transaction._rollback_exception.orig.pgerror})
        return rtn

    return wrapper


def jsonify(func):
    def wrapper(*args, **kwargs):
        rtn = func(*args, **kwargs)
        result = None
        if isinstance(rtn, list):
            result = []
            for item in rtn:
                print("list is here: ", rtn)
                result.append(model_to_dict(item))
            result = {"result": result}
        else:
            result = model_to_dict(rtn)
            print("json result is : ", result)
        return result

    return wrapper


def pass_data(func):
    def wrapper(*args, **kwargs):
        if request.json:
            kwargs['data'] = request.json
        elif request.forms:
            my_data = {}
            data_list = request.forms.dict
            for key in data_list.keys():
                my_data[key] = data_list[key][0]
            if (request.files != None) and (request.files.dict != None):
                my_data['image'] = request.files.dict.get('image')

            kwargs['data'] = my_data

        rtn = func(*args, **kwargs)
        return rtn

    return wrapper


def Now():
    now = time.mktime(datetime.datetime.now().timetuple())
    return int(now)


def Http_error(code, message):
    if isinstance(message,str):
        message = {'error':message}
    result = HTTPResponse(body=json.dumps(message), status=code,
        headers = {'Content-type': 'application/json'})
    return result


def value(name, default):
    return environ.get(name) or default


def validate_token(id, db_session):
    result = db_session.query(APP_Token).filter(APP_Token.id == id).first()
    if result is None or result.expiration_date < Now():
        raise Http_error(401,{"id":LogMsg.TOKEN_INVALID} )
    return result


def file_mime_type(filename):
    # m = magic.open(magic.MAGIC_MIME)
    m = magic.from_file(filename, mime=True)
    print(m)

    return str(m)


def check_schema(required_list,data_keys):
    required = set(required_list)
    keys= set(data_keys)

    result = required.issubset(keys)

    if result==False:
        raise Http_error(400,{'data':'{} are required'.format(required_list)})

    return result



