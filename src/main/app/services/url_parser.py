import re
import json


class UrlParser():

    def __init__(self):
        pass

    @staticmethod
    def parse_url(url):
        pattern = r'''
            (?P<driver>^[^:]+)://
            (?:(?P<username>[^:@]+)(?::(?P<password>[^@]+))?@)?
            (?P<hostname>[^/:;]+)
            (?:\:(?P<port>\d+))?
            (?:/(?P<dbname>[^;]+))?
            (?:;(?P<params>.*))?
        '''
        match = re.match(pattern, url, flags=re.VERBOSE)

        if not match:
            return None
        
        result = match.groupdict()
        result['params']   = UrlParser._get_params_from_json(result)
        result['password'] = '' if result['password'] is None else result['password']
        result['dbname']   = '' if result['dbname'] is None else result['dbname']
        result['port']     = None if result['port'] is None else result['port']

        return result
   
    @staticmethod
    def  _get_params_from_json(parsed_url):
        if parsed_url['params']:
            try:
                return json.loads(parsed_url['params'])
            except json.JSONDecodeError:
                print("Invalid JSON in params")
                return {}
        else:
            return {}

