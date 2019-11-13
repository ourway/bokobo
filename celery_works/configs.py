class BaseConfig:
    CELERY_BROKER = 'pyamqp://<username>:<password>@<host>//'
    CELERY_BACKEND = 'db+postgresql://<libuser>:<libpass>@<localhost>/<online_library>'

    RETRIES_COUNT = 1
    RETRY_DELAY = 2
    BEAT_INTERVAL = 10

class Messaging(BaseConfig):
    RETRIES_COUNT = 1
    RETRY_DELAY = 1

    GENERAL_EXCHANGE = 'general'
    MAIN_EXCHANGE = 'Jam_e_Jam.general'
    MAIN_ROUTING_KEY = 'general'
    MESSAGING_QUEUE = 'general'

    XMPP_EXCHANGE = 'xmpp'
    XMPP_ROUTING_KEY = 'xmpp'
    XMPP_QUEUE = 'xmpp'
    XMPP_CLIENT_USERNAME = ''
    XMPP_CLIENT_PASSWORD = ''
    XMPP_SERVER_ADDRESS = '127.0.0.1'
    XMPP_SERVER_PORT = 5222

    SMTP_EXCHANGE = 'smtp'
    SMTP_ROUTING_KEY = 'smtp'
    SMTP_QUEUE = 'smtp'
    SMTP_CLIENT_USERNAME = ''
    SMTP_CLIENT_PASSWORD = ''
    SMTP_SERVER_ADDRESS = 'mail.Jam_e_Jam.net'
    SMTP_SERVER_PORT = 25

    SMS_EXCHANGE = 'sms'
    SMS_ROUTING_KEY = 'sms'
    SMS_QUEUE = 'sms'

    SENTRY_DSN = 'https://<key>:<secret>@sentry.io/<project>'

class BookGenerate(BaseConfig):

    BOOK_GENERATE_EXCHANGE = 'book_generate'
    BOOK_GENERATE_KEY = 'book_generate'
    BOOK_GENERATE_QUEUE = 'book_generate'

    SENTRY_DSN = 'https://<key>:<secret>@sentry.io/<project>'


class AppConfigsUpdater(BaseConfig):
    EXCHANGE = 'ex_app_configs_updater'
    UPDATE_CONFIGS_QUEUE = 'q_app_configs_updater.update_configs'
    REDIS_WATCHER_QUEUE = 'q_app_configs_updater.redis_watcher'

    REDIS_WATCHER_BEAT_INTERVAL = 10
    UPDATE_CONFIGS_BEAT_INTERVAL = 10

    SENTRY_DSN = 'https://<key>:<secret>@sentry.io/<project>'
