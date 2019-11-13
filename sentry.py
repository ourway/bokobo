from sentry_sdk import init, capture_message, capture_exception
from sentry_sdk.integrations.bottle import BottleIntegration

sentry_client = init("https://d8e7b626ed4c46b388351e3b62ce4ced@sentry.io/1816701",
    integrations=[BottleIntegration()])


capture_message("Hello World")  # Will create an event.

capture_exception(Exception("This is an example of an error message."))