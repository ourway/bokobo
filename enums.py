import enum
from helper import Http_error
from messages import Message


class Roles(enum.Enum):
    Author = 'Author'
    Writer = 'Writer'
    Translator = 'Translator'
    Press = 'Press'
    Contributer = 'Contributer'
    Designer = 'Designer'
    Narrator = 'Narrator'


class BookTypes(enum.Enum):
    DVD = 'DVD'
    Audio = 'Audio'
    Hard_Copy = 'Hard_Copy'
    Pdf = 'Pdf'
    Epub = 'Epub'


class Genre(enum.Enum):
    Comedy = 'Comedy'
    Drama = 'Drama'
    Romance = 'Romance'
    Social = 'Social'
    Religious = 'Religious'
    Historical = 'Historical'
    Classic = 'Classic'
    Science = 'Science'


class ReportComment(enum.Enum):
    Personal = 'Personal'
    Invalid_Content = 'Invalid_Content'
    General = 'General'


class AccountTypes(enum.Enum):
    Main = 'Main'
    Star = 'Star'
    Discount = 'Discount'
    Postpaid = 'Postpaid'
    Prepaid = 'Prepaid'


class OrderStatus(enum.Enum):
    Created = 'Created'
    Invoiced = 'Invoiced'
    Canceled = 'Canceled'
    Postponed = 'Postponed'


class Permissions(enum.Enum):
    IS_OWNER = 'IS_OWNER'
    ACCOUNT_ADD_PREMIUM = 'ACCOUNT_ADD_PREMIUM'
    ACCOUNT_EDIT_PREMIUM = 'ACCOUNT_EDIT_PREMIUM'
    ACCOUNT_DELETE_PREMIUM = 'ACCOUNT_DELETE_PREMIUM'
    ACCOUNT_GET_PREMIUM = 'ACCOUNT_GET_PREMIUM'

    LIBRARY_ADD_PREMIUM = 'LIBRARY_ADD_PREMIUM'
    LIBRARY_EDIT_PREMIUM = 'LIBRARY_EDIT_PREMIUM'
    LIBRARY_DELETE_PREMIUM = 'LIBRARY_DELETE_PREMIUM'
    LIBRARY_GET_PREMIUM = 'LIBRARY_GET_PREMIUM'

    RATE_DELETE_PREMIUM = 'RATE_DELETE_PREMIUM'
    RATE_EDIT_PREMIUM = 'RATE_EDIT_PREMIUM'

    BOOK_ADD_PREMIUM = 'BOOK_ADD_PREMIUM'
    BOOK_EDIT_PREMIUM = 'BOOK_EDIT_PREMIUM'
    BOOK_DELETE_PREMIUM = 'BOOK_DELETE_PREMIUM'
    BOOK_ADD_PRESS = 'BOOK_ADD_PRESS'
    BOOK_EDIT_PRESS = 'BOOK_EDIT_PRESS'
    BOOK_DELETE_PRESS = 'BOOK_DELETE_PRESS'

    COMMENT_ADD_PREMIUM = 'COMMENT_ADD_PREMIUM'
    COMMENT_EDIT_PREMIUM = 'COMMENT_EDIT_PREMIUM'
    COMMENT_DELETE_PREMIUM = 'COMMENT_DELETE_PREMIUM'
    COMMENT_GET_PREMIUM = 'COMMENT_GET_PREMIUM'
    COMMENT_ADD = 'COMMENT_ADD'
    COMMENT_EDIT = 'COMMENT_EDIT'
    COMMENT_DELETE = 'COMMENT_DELETE'
    COMMENT_GET = 'COMMENT_GET'
    COMMENT_DELETE_PRESS = 'COMMENT_DELETE_PRESS'

    TRANSACTION_ADD_PREMIUM = 'TRANSACTION_ADD_PREMIUM'
    TRANSACTION_DELETE_PREMIUM = 'TRANSACTION_DELETE_PREMIUM'
    TRANSACTION_GET_PREMIUM = 'TRANSACTION_GET_PREMIUM'

    COMMENT_ACTION_DELETE_PREMIUM = 'COMMENT_ACTION_DELETE_PREMIUM'
    COMMENT_ACTION_DELETE_PRESS = 'COMMENT_ACTION_DELETE_PRESS'

    FOLLOW_DELETE_PREMIUM = 'FOLLOW_DELETE_PREMIUM'

    ORDER_CHECKOUT_PREMIUM = 'ORDER_CHECKOUT_PREMIUM'
    ORDER_ADD_PREMIUM = 'ORDER_ADD_PREMIUM'
    ORDER_ADD_PRESS = 'ORDER_ADD_PRESS'
    ORDER_GET_PREMIUM = 'ORDER_GET_PREMIUM'
    ORDER_EDIT_PREMIUM = 'ORDER_EDIT_PREMIUM'
    ORDER_DELETE_PREMIUM = 'ORDER_DELETE_PREMIUM'

    ORDER_ITEM_GET_PREMIUM = 'ORDER_ITEM_GET_PREMIUM'
    ORDER_ITEM_EDIT_PREMIUM = 'ORDER_ITEM_EDIT_PREMIUM'
    ORDER_ITEM_DELETE_PREMIUM = 'ORDER_ITEM_DELETE_PREMIUM'

    PRICE_ADD_PREMIUM = 'PRICE_ADD_PREMIUM'
    PRICE_GET_PREMIUM = 'PRICE_GET_PREMIUM'
    PRICE_EDIT_PREMIUM = 'PRICE_EDIT_PREMIUM'
    PRICE_DELETE_PREMIUM = 'PRICE_DELETE_PREMIUM'
    PRICE_ADD_PRESS = 'PRICE_ADD_PRESS'
    PRICE_EDIT_PRESS = 'PRICE_EDIT_PRESS'
    PRICE_DELETE_PRESS = 'PRICE_DELETE_PRESS'

    PERSON_ADD_PREMIUM = 'PERSON_ADD_PREMIUM'
    PERSON_EDIT_PREMIUM = 'PERSON_EDIT_PREMIUM'
    PERSON_DELETE_PREMIUM = 'PERSON_DELETE_PREMIUM'
    PERSON_GET_PREMIUM = 'PERSON_GET_PREMIUM'

    USER_DELETE_PREMIUM = 'USER_DELETE_PREMIUM'
    USER_GET_PREMIUM = 'USER_GET_PREMIUM'
    USER_EDIT_PREMIUM = 'USER_EDIT_PREMIUM'

    DISCUSSION_GROUP_PREMIUM = 'DISCUSSION_GROUP_PREMIUM'
    DISCUSSION_MEMBER_PREMIUM = 'DISCUSSION_MEMBER_PREMIUM'


def check_enums(data, enum_class):
    for type in data:
        if type not in enum_class.__members__:
            raise Http_error(404, Message.INVALID_ENUM)
    return data


def str_genre(genre_list):
    res = []
    if genre_list is None:
        genre_list = []
    for genre in genre_list:
        res.append((getattr(Genre, genre)).value)
    return res


def str_type(btype):
    if btype is not None:
        return (getattr(BookTypes, btype)).value
    else:
        return ''


def str_role(role):
    if role is not None:
        return (getattr(Roles, role)).value
    else:
        return ''


def str_report(report):
    if report is not None:
        if isinstance(report, str):
            return report
        else:
            return report.value
    else:
        return None


def check_enum(type, enum_class):
    if type not in enum_class.__members__:
        raise Http_error(404, Message.INVALID_ENUM)

    return type


def str_account_type(account_type):
    if account_type is not None:
        if isinstance(account_type, str):
            return account_type
        else:
            return account_type.value
    else:
        return None
