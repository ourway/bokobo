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





def check_enums(data,enum_class):
    for type in data:
        if type not in enum_class.__members__:
            raise Http_error(404,Message.MSG19)
    return data

def str_genre(genre_list):
    res = []
    if genre_list is None:
        genre_list=[]
    for genre in genre_list:
        res.append((getattr(Genre,genre)).value)
    return res


def str_type(btype):
    if btype is not None:
        return (getattr(BookTypes,btype)).value
    else:
        return ''

def str_role(role):
    if role is not None:
        return (getattr(Roles,role)).value
    else:
        return ''

def str_report(report):
    if report is not None:
        if isinstance(report,str):
            return report
        else:
            return report.value
    else:
        return None

def check_enum(type,enum_class):
    if type not in enum_class.__members__:
        raise Http_error(404, Message.MSG19)

    return type


def str_account_type(account_type):
    if account_type is not None:
        if isinstance(account_type,str):
            return account_type
        else:
            return account_type.value
    else:
        return None