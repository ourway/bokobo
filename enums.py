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