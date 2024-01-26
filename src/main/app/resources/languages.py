import json
from app.services.metaclass import SingletonBase


FILE_NAME_OF_LANGUAGES = './app/resources/languages.json'

class Languages(metaclass=SingletonBase):

    def __init__(self):

        with open(FILE_NAME_OF_LANGUAGES, "r", encoding='utf-8') as file:
            content = file.read()

        language_items = json.loads(content)['languages']
        languages = [language_item['name'] for language_item in language_items ]
        language_sorted = sorted( zip(languages, language_items) )

        languages, language_items = zip(*language_sorted)

        self._languages = list( language_items )
        
    def __len__(self):
        return len(self._languages)
    
    def get_paginated_language_codes(self, page = 0, count_per_page = 9):

        if page < 1 or count_per_page < 1:
            raise ValueError("Page and count_per_page should be positive integers.")
    
        start_index = (page - 1) * count_per_page
        end_index = start_index + count_per_page
        
        page_items = self._languages[start_index:end_index]
        
        return [language_item['code'] for language_item in page_items]
    
    def get_language_by_code(self, code):

        for language_item in self._languages:
            if(code == language_item['code']):
                return language_item
        
        