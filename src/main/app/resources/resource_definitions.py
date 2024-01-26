
from threading import Lock
from string import Template
import json
import os

from app.telegram_bot.bot_interface import (
    tgButton,
    tgInlineMenu
)


DEFAULT_LANGUAGE = 'en'
STR_DEFINITION_FILE_NAME = './app/resources/resource_definitions.json'

class SingletonDefinitionMeta(type):
    
    _instances_by_language = {}
    _default_language      = ''
    _lock      = Lock()
    
    def __call__(cls, language=DEFAULT_LANGUAGE, *args, **kwargs):
        
        with cls._lock:

            if(cls._default_language == ''):
                cls._default_language = language
            
            if(language not in cls._instances_by_language):
                instance = super().__call__(language, *args, **kwargs)
                cls._instances_by_language[language] = instance
            
            return cls._instances_by_language[language]
    
class DefinitionsMetaclass(SingletonDefinitionMeta):

    def __init__(cls, name, bases, attrs):

        str_vars = cls._load_definitions()
        assert str_vars  is not None, 'Class {} do not have attribute __varables'.format(name) 

        for key, value in str_vars.items():

            assert value.get('type') is not None, f'Key "{key}" do not have property "type"'

            private_name = "_{}".format(key)
            setattr(cls, private_name, value)
            
            if(value['type'] == 'string' or value['type'] == 'command'):
                DefinitionsMetaclass._add_string_property(cls, key, private_name, value)
            elif(value['type'] == 'button'):
                DefinitionsMetaclass._add_button_property(cls, key, private_name)
            elif(value['type'] == 'menu'):
                DefinitionsMetaclass._add_menu_property(cls, key, private_name)
            elif(value['type'] == 'languages'):
                DefinitionsMetaclass._add_supported_languages(cls, key, private_name)


        super().__init__(name, bases, attrs)

    @staticmethod
    def _add_supported_languages(cls, property_name: str, private_name: str ):
        
        def make_language_getter(private_name):
            def getter(self):
                return self._get_supported_language(private_name)

            return getter

        getter_fn = property(make_language_getter(private_name))
        setattr(cls, property_name, getter_fn)

    @staticmethod
    def _add_menu_property(cls, property_name: str, private_name: str):

        def make_menu_getter(private_name):

            def getter(self):
                
                return self._get_dynamic_value_menu(private_name)

            return getter

        getter_fn = property(make_menu_getter(private_name))

        setattr(cls, property_name, getter_fn)
    

    @staticmethod
    def _add_button_property(cls, property_name: str,private_name: str):

        def make_button_getter(private_name):

            def button_getter(self):
                
                return self._get_dynamic_value_button(private_name)

            return button_getter

        getter_fn = property(make_button_getter(private_name))
        setattr(cls, property_name, getter_fn)
    
    @staticmethod    
    def _add_string_property(cls, property_name: str, private_name: str, value):

        if( value.get('is_using_format', False)  ):
                
            def make_getter_with_params(private_name):
                def getter_with_params(self, params = {}):
                    return self._get_dynamic_value_string_using_format(private_name, params)
                return getter_with_params

            getter_fn = make_getter_with_params(private_name)

        else:

            def make_getter(private_name):
                def getter(self):
                    return self._get_dynamic_value_string(private_name)
                return getter

            getter_fn = property(make_getter(private_name))

        setattr(cls, property_name, getter_fn)

    def _load_definitions(cls) -> dict:

        with open(STR_DEFINITION_FILE_NAME, "r", encoding='utf-8') as file:
            content = file.read()

        return  json.loads(content)

class ResourceDefinition(metaclass=DefinitionsMetaclass):

    __varibles = {}

    def __init__(self, language = DEFAULT_LANGUAGE):

        self._language = language
        self._buttons_instances  = {}
        self._menu_instances     = {}
       
    def _get_supported_language(self, name):

        attr_value = getattr(self, name)

        return attr_value['lang']

    def _get_dynamic_value_string(self, name):

        attr_value = getattr(self, name)

        langauges = [self._language, 'default', DEFAULT_LANGUAGE]

        for item_language in langauges:
            string = attr_value['str'].get(item_language)

            if(string is not None):
                break

        if( isinstance(string, list) ):
            string = '\n'.join(string)

        return string

    def _get_dynamic_value_string_using_format(self, name, params = {}):

        string = self._get_dynamic_value_string(name)
        str_template = Template(string)

        return str_template.substitute(**params)

    def _get_dynamic_value_button(self, name):

        property_value = getattr(self, name)
        action_id      = property_value['action_id']
        roles          = property_value.get('roles', [])

        if(self._buttons_instances.get(action_id) is None ):

            caption_property_name = property_value['caption']
            caption = getattr(self, caption_property_name )
            button  = tgButton(caption, action_id, {}, roles )
            self._buttons_instances[action_id] = button

        return self._buttons_instances[action_id]

    def _get_dynamic_value_menu(self, name ):

        property_value = getattr(self, name)
        menu_id      = property_value['menu_id']

        if(self._menu_instances.get(menu_id) is None ):
            
            menu  = tgInlineMenu(menu_id)


            row_buttons = self._get_menu_buttons_row(property_value.get('buttons', {}))
            row_buttons_inline = self._get_menu_buttons_row(property_value.get('buttons_inline', {}))

            menu.set_buttons(row_buttons_inline, 'inline')
            menu.set_buttons(row_buttons, 'keyboard')
            
            self._menu_instances[menu_id] = menu

        return self._menu_instances[menu_id]

    def _get_menu_buttons_row(self, menu_buttons):

        buttons_rows       = {}

        for key, value in menu_buttons.items():

            buttons = [ getattr(self, def_button) for def_button in value   ]
            buttons_rows[int(key)] = buttons

        return buttons_rows
  
    def get_language(self):
        return self._language

    
