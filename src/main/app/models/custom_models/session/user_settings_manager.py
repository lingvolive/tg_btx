
from app.resources.languages import Languages


class UserSettingsManager:
    def __init__(self, session) -> None:

        if(session.data is None):
            session.data = {}
            
        self._data = session.data
        self._default_language_code = 'en'
        self._settings_for_reset    = {}

    def set_setting(self, setting_name, value):
        self._data[setting_name] = value
    
    def get_setting(self, setting_name, def_value = None, type_func = None):
        value =  self._data.get(setting_name, def_value)
        if(type_func is not None):
            value = type_func(value)

        return value

    def reset(self, resettings_settings):
        
        for key, value in resettings_settings.items():
            self._data[key] = value
   
    def push_state_to_history(self, state_id):
        self._data.setdefault('steps_history', [])
        self._data['steps_history'].append(state_id)

    def pop_last_state_from_history(self):
        self._data.setdefault('steps_history', [])
        return self._data['steps_history'].pop()
    
    def _get_language_settings(self):

        language_settings = self._data.get(
            'translator_languages', 
            None
        )

        if(language_settings is None):
            language_settings = {'languages':[], 'default_language_code':''}
            self._data['translator_languages'] = language_settings

        if len(language_settings['languages']) == 0:
            self.add_or_remove_language(self._default_language_code, language_settings)

        return language_settings

    def get_language_codes(self):

        language_settings = self._get_language_settings()
        
        return [language_item['code'] for language_item in language_settings['languages'] ]
    
    def get_default_language_code(self):

        language_settings = self._get_language_settings()
        
        return language_settings['default_language_code']
    
    def set_default_language(self, language_code):

        language_settings = self._get_language_settings()
        language_settings['default_language_code'] = language_code

    def add_or_remove_language(self, language_code, language_settings = None):
       
        language_settings   = language_settings or self._get_language_settings()
        is_language_deleted = False

        for idx, language_item in enumerate(language_settings['languages']):
            
            if language_item['code'] == language_code:
               
                del language_settings['languages'][idx]
                is_language_deleted = True

        self._update_default_language_code(language_settings)

        if not is_language_deleted:
            
            languages = Languages()
            language_settings['languages'].append(languages.get_language_by_code(language_code))
            language_settings['default_language_code'] = language_code

    def _update_default_language_code(self, language_settings):

        if len(language_settings['languages']) > 0:
            language_settings['default_language_code'] = language_settings['languages'][-1]['code']
        else:
            language_settings['default_language_code'] = ''
