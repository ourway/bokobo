from configs import SIGNUP_USER
from helper import Http_error, model_to_dict
from log import  logger, Msg
from app_redis import app_redis as redis
from repository.user_repo import check_by_id

from user.controllers.user import add as add_user
from user.controllers.person import add as add_person
from pudb import set_trace

def signup(data,db_session,*args,**kwargs):
    set_trace()
    # logger.info(Msg.START,extra={data})
    #
    # logger.debug(Msg.CHECK_REDIS_FOR_EXISTANCE)

    cell_no = data.get('cell_no')

    signup_token = redis.get(cell_no)
    if signup_token is None:
        logger.error(Msg.REGISTER_KEY_DOESNT_EXIST)
        raise Http_error(404, {"signup_token": Msg.TOKEN_KEY_DOESNT_EXIST})

    signup_token = signup_token.decode("utf-8")
    if signup_token != data.get('signup_token'):
        logger.error(Msg.REGISTER_KEY_INVALID)
        raise Http_error(400, {"signup_token": Msg.TOKEN_INVALID})



    user_data = data.get('user')
    person_data = data.get('profile')

    person_data.update({'cell_no':cell_no})

    person = add_person(db_session,person_data,SIGNUP_USER)

    user_data.update({'person_id':person.id})
    user = add_user(db_session,user_data,SIGNUP_USER)

    result = {'user':model_to_dict(user),'person':model_to_dict(person)}

    return result




