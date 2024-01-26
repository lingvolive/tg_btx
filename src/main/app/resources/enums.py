from enum import  IntFlag, auto, Enum

class tgMessageTypes(Enum):

    TEXT    = 'text'
    COMMAND = 'command'
    INLINE  = 'inline'
    AUDIO   = 'audio'
    VOICE   = 'voice'
    DOCUMENT   = 'doc'
    PHOTO       = 'photo'

    CUSTOM_INLINE = 'custom_inline'


class processorsTypes(IntFlag):

    NONE     = auto()
    NOT_IMPLEMENTED = auto()
    LOGIN_INPUT_EMAIL = auto()
    LOGIN_INPUT_FULL_NAME = auto()
    LOGIN_INPUT_PHONE = auto()
    LOGIN_WAIT_CONFIRMATION = auto()
    COMMAND_START       = auto()
    COMMAND_ADMIN       = auto()
    SET_ADMIN       = auto()
    HELP     = auto()
    MAIN     = auto()
    SETTINGS           = auto()
    SETTINGS_LANGUAGE  = auto()
    PROFILE_VIEW  = auto()
    USER_MANAGE  = auto()
    CHOOSE_USER  = auto()
    USER_MANAGE_SET_ROLES  = auto()
    CHOOSE_MANAGERS  = auto()
    SEND_DAILY_REPORT = auto()
    LABOR_COST_REPORT = auto()
    LABOR_COST_REPORT_INPROGRESS = auto()
    LABOR_COST_REPORT_READY = auto()
    LABOR_COST_REPORT_FILTERS = auto()
    LABOR_COST_REPORT_FILTER_PERIOD = auto()
    LABOR_COST_REPORT_FILTER_PROJECT = auto()
    LABOR_COST_REPORT_FILTER_EMPLOYEE = auto()
    LABOR_COST_REPORT_FILTER_RESET = auto()
    
    LOGIN    = auto()
   