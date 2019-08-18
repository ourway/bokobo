from comment.models import Comment
from helper import Http_error, Http_response
from messages import Message


def delete_book_comments(book_id,db_session):

    try:
       comment =  db_session.query(Comment).filter(Comment.book_id == book_id).first()
       if comment is not None:
           db_session.query(Comment).filter(Comment.book_id == book_id).delete()

    except:
        raise Http_error(404,Message.MSG20)

    return Http_response(204,True)

def get_comment(id,db_session,**kwargs):

    try:
        result = db_session.query(Comment).filter(Comment.id == id).first()

    except:
        Http_error(404,Message.MSG20)
    return result
