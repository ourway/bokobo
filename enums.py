import enum
from helper import Http_error
from messages import Message


class Roles(enum.Enum):
    Author = 'author'
    Writer = 'writer'
    Translator = 'translator'
    Press = 'press'
    Contributer = 'contributer'
    Designer = 'designer'


class BookTypes(enum.Enum):
    DVD = 'dvd'
    Audio = 'audio'
    Hard_Copy = 'hard_copy'
    Pdf = 'pdf'
    Epub = 'epub'

class Genre(enum.Enum):
    Comedy = 'comedy'
    Drama = 'drama'
    Romance = 'romance'
    Social = 'social'
    Religious = 'religious'
    Historical = 'historical'



def check_enums(data,enum_class):
    for type in data:
        if type not in enum_class.__members__:
            raise Http_error(404,Message.MSG19)
    return data