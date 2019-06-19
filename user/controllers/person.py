import os
from uuid import uuid4

from helper import model_to_dict, Now, value, Http_error
from  log import logger,Msg
from ..models import Person
from repository.person_repo import person_cell_exists,person_mail_exists

save_path = os.environ.get('save_path')


def add(db_session,data,username):

    if person_cell_exists(db_session,data.get('cell_no')):
        raise Http_error(409,Msg.PERSON_EXISTS.format('cell_no'))

    if person_mail_exists(db_session,data.get('email')):
        raise Http_error(409,Msg.PERSON_EXISTS.format('email'))

    # logger.info(Msg.START,extra={'data':data,'user':username})

    model_instance = Person()
    model_instance.id = str(uuid4())
    model_instance.name = data.get('name')
    model_instance.last_name = data.get('last_name')
    model_instance.address = data.get('address')
    model_instance.phone = data.get('phone')
    model_instance.email = data.get('email')
    model_instance.cell_no = data.get('cell_no')
    model_instance.creation_date = Now()
    model_instance.creator = username
    model_instance.version = 1

    images = data.get('image',[])
    image = None
    if len(images)> 0:
        image = images[0]

    if image:
        image.filename = str(uuid4())
        model_instance.image = image.filename

        image.save(save_path)
        del (data['image'])



    # logger.debug(Msg.DATA_ADDITION)

    db_session.add(model_instance)

    # logger.debug(Msg.DB_ADD,extra = {'person':model_to_dict(model_instance)})

    # logger.info(Msg.END)
    return model_instance