from sentry_sdk import init, capture_message

init("https://d8e7b626ed4c46b388351e3b62ce4ced@sentry.io/1816701")


capture_message("Hello World")  # Will create an event.

