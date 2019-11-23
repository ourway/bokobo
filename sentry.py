from raven.base import Raven
from sentry_sdk import init, capture_message, capture_exception
from sentry_sdk.integrations.bottle import BottleIntegration

import logging
from sentry_sdk.integrations.logging import LoggingIntegration

# All of this is already happening by default!
sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)


sentry_client = init(dsn='https://d8e7b626ed4c46b388351e3b62ce4ced@sentry.io/1816701',
    integrations=[BottleIntegration(),sentry_logging])





capture_message("Hello World")  # Will create an event.

capture_exception(Exception("This is an example of an error message."))