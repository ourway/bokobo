from comment.models import Comment
from helper import Http_error, Http_response
from log import logger, LogMsg
from messages import Message
from repository.action_repo import delete_comment_actions_internal


def delete_book_comments(book_id,db_session):

    try:
       comments =  db_session.query(Comment).filter(Comment.book_id == book_id).all()
       if comments is not None:
           for item in comments:
               logger.debug(LogMsg.COMMENT_DELETE_ACTIONS, item.id)
               delete_comment_actions_internal(db_session, item.id)
               db_session.delete(item)
    except:
        raise Http_error(404,Message.NOT_FOUND)

    return Http_response(204,True)

def get_comment(id,db_session,**kwargs):

    try:
        result = db_session.query(Comment).filter(Comment.id == id).first()

    except:
        Http_error(404,Message.NOT_FOUND)
    return result
