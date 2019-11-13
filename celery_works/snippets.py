import os
import ast
import json
import base64
import logging
from importlib import import_module

import raven
import celery
from datetime import datetime
from khayyam import JalaliDate
from jinja2 import Environment, BaseLoader
from celery.utils.log import get_task_logger
from raven.contrib.celery import register_signal, register_logger_signal


def convert_epoch_to_jalali(epoch):
    result = str(epoch_to_jalali(epoch))
    return result.replace('-', '/')


def remove_duplicates(l):
    return list(set(l))


def remove_null_values(values):
    if isinstance(values, list):
        return list(filter(None, values))
    return values


template_env = Environment(loader=BaseLoader, extensions=['jinja2.ext.do'])
template_env.globals.update(remove_duplicates=remove_duplicates)
template_env.globals.update(remove_null_values=remove_null_values)
template_env.globals.update(convert_epoch_to_jalali=convert_epoch_to_jalali)


def load_template(template_string, convert_to_dict=True, **params):
    # try:
    template = template_env.from_string(template_string)
    template_body = template.render(**params)

    if not convert_to_dict:
        return template_body

    result = ast.literal_eval(template_body)
    return result

    # except Exception as exc:
    #     exception_detail = str(exc)
    #     lineno = exc.lineno if hasattr(exc, 'lineno') else 'NONE'
    #     e_msg = exc.message if hasattr(exc, 'message') else exception_detail
    #
    #     msg = 'invalid template: line:' + str(lineno) + ' - ' + e_msg
    #
    #     if logger.level_is_warning:
    #         logger.warning(msg, func_name=func_name, func_path=func_path,
    #                        extra_details={'template': template_string,
    #                                       'error': exception_detail})


def get_celery_app(sentry_dsn):
    class Celery(celery.Celery):
        def on_configure(self):
            client = raven.Client(sentry_dsn)

            # register a custom filter to filter out duplicate logs
            register_logger_signal(client)

            # hook into the Celery error handler
            register_signal(client)

    return Celery


def string_to_base64(string):
    result = base64.b64encode(string.encode())
    return result.decode(encoding='utf-8')


def create_basic_auth_token(username, password):
    encoded_credentials = string_to_base64('{}:{}'.format(username, password))
    return 'BASIC {}'.format(encoded_credentials)


def logger(msg, details=None, log_level=logging.INFO):
    celery_logger = get_task_logger(__name__)

    if log_level == logging.CRITICAL:
        __logger = celery_logger.critical
        __log_level = logging.CRITICAL
    elif log_level == logging.ERROR:
        __logger = celery_logger.error
        __log_level = logging.ERROR
    else:
        __logger = celery_logger.info
        __log_level = logging.INFO

    if celery_logger.isEnabledFor(__log_level):
        log_msg = '###{msg}  ###{details}'.format(msg=msg,
                                                  details=json.dumps(details))
        __logger(log_msg)


def epoch_to_datetime(epoch):
    return datetime.utcfromtimestamp(epoch)


def epoch_to_jalali(epoch):
    return JalaliDate(epoch_to_datetime(epoch))

