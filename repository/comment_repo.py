from comment.models import Comment
from helper import Http_error
from messages import Message


def delete_book_comments(book_id,db_session):

    try:
        db_session.query(Comment).filter(Comment.book_id == book_id).delete()

    except:
        raise Http_error(404,Message.MSG20)

    return {}
