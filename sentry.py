from sentry_sdk import init, capture_message

init("https://d8e7b626ed4c46b388351e3b62ce4ced@sentry.io/1816701")

division_by_zero = 1 / 0

capture_message("Hello World")  # Will create an event.

raise ValueError()  # Will also create an event.