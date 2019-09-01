from comment.models import CommentAction


def delete_comment_actions_internal(db_session, comment_id):
    db_session.query(CommentAction).filter(
        CommentAction.comment_id == comment_id).delete()
    return True
