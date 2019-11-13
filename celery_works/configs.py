class BaseConfig:
    CELERY_BROKER = 'pyamqp://guest@localhost//'
    CELERY_BACKEND = 'db+postgresql://libuser:libpass@localhost/celery'

    RETRIES_COUNT = 1
    RETRY_DELAY = 2
    BEAT_INTERVAL = 10


class BookGenerate(BaseConfig):

    BOOK_GENERATE_EXCHANGE = 'book_generate'
    BOOK_GENERATE_KEY = 'book_generate'
    BOOK_GENERATE_QUEUE = 'book_generate'

    SENTRY_DSN = 'https://<key>:<secret>@sentry.io/<project>'
