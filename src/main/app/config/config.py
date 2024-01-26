import configparser
from   dataclasses import  dataclass
import os
from app.services.metaclass import SingletonBase


# Define a data class to store the configuration for the Telegram Bot
@dataclass
class TgBot:
    # Store the token used to authenticate the bot
    token: str
    admin_password : str
    language: str
    path_files : str

# Define a data class to store the configuration for the database
@dataclass
class DB:
    # Store the connection string used to connect to the database
    db_conn_str: str
    

@dataclass
class Log:
    log_file: str
    log_level : str
    log_rotation_interval: str
    log_fmt : str
    log_date_fmt : str

@dataclass
class Btx:
    url_api_batch: str
    

class Config(metaclass=SingletonBase):
  
    tg_bot: TgBot 
    db    : DB  
    log   : Log
    btx   : Btx

    def __init__(
            self, 
            config_store_type : str = 'env', 
            config_file_name : str = None,
            commandline_args : dict = {} 
        ):
        """
        Initialize the Config class. 
        
        :param config_store_type: The type of configuration store to use. Can be either 'file' or 'env'.
        :param config_file_name: The name of the configuration file, if the config_store_type is 'file'.
        """

        self._confg_file_name = config_file_name
        self._test_mode       = commandline_args.get('test_mode', False)
        
        # Ensure that the config_store_type is either 'file' or 'env'
        if config_store_type not in ('file', 'env'):
            raise ValueError(f'Unsupported config store type: {config_store_type}')

        if(config_store_type == 'file' ):
            self._load_config_from_file(config_file_name)
        elif(config_store_type == 'env' ):
            self._load_config_from_env()

    def _load_config_from_env(self):
        """
        Load the configuration from environment variables.
        """

        name_bot_token_key = 'BOT_TOKEN_TEST' if self._test_mode else 'BOT_TOKEN'
        
        self.tg_bot = TgBot( 
            token  = os.environ.get(name_bot_token_key), 
            language = os.environ.get('LANGUAGE'),
            path_files = os.environ.get('PATH_FILES'),
            admin_password = os.environ.get('ADMIN_PASSWORD')

        )
        
        self.db = DB( 
            db_conn_str = os.environ.get('DB_CONN_STR'),
             
        )

        self.log = Log(

            log_file  = os.environ.get('TG_LOG_FILE_NAME'),
            log_level = os.environ.get("TG_LOG_LEVEL"),
            log_rotation_interval = os.environ.get("TG_LOG_ROTATION_INTERVAL"),
            log_fmt = os.environ.get("TG_LOG_FMT"),
            log_date_fmt = os.environ.get("TG_LOG_DATE_FMT"),
       
        )

        self.btx = Btx(
            url_api_batch=os.environ.get('BTX_URL_API_BATCH')

        )

    def _load_config_from_file(self, config_file_name : str):
        """
        Load the configuration from a file.
        
        :param config_file_name: The name of the configuration file.
        """

        config = configparser.ConfigParser()
        config.read( config_file_name )
   
        self.tg_bot = TgBot( **config['tg_bot'] )
        self.db     = DB( **config['db'] )
        
         
         


 