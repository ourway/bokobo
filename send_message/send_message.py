import logging


from helper import value



def send_message(data):
    message = {'Text': str(data.get('message')), 'SMSC': {'Location': 1},
               'Number': str(data.get('cell_no'))}
    print(message)
    return data