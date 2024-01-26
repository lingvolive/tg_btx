
from app.resources.enums import processorsTypes
from app.processors.state_processor import StateProcessor
from app.processors.custom_processors.sp_none import StateProcessorNone
from app.processors.custom_processors.sp_profile import (
    StateProcessorLoginEmail,
    StateProcessorLoginFullName,
    StateProcessorLoginPhone,
    StateProcessorLoginWaitConfirmation,
    StateProcessorSetAdmin,
    StateProcessorProfileView,
)

from app.processors.custom_processors.sp_user_management import (
    StateProcessorUserManagementMenu,
    StateProcessorUserManagementSetRoles,
)
from app.processors.custom_processors.sp_choose_user import (
    StateProcessorChooseUser,
    StateProcessorChooseManager,
    StateProcessorChooseProjectFilter,
    StateProcessorChooseEmployeeFilter
)

from app.processors.custom_processors.sp_commands import (
    StateProcessorCommandStart,
    StateProcessorCommandAdmin
)

from app.telegram_bot.bot_interface import tgButton
from app.resources.resource_definitions import ResourceDefinition

from app.processors.custom_processors.sp_help import State_processor_help
from app.processors.custom_processors.sp_main import StateProcessorMainMenu
from app.processors.custom_processors.sp_not_implemented import StateProcessorNotImplemented

from app.processors.custom_processors.sp_settings import StateProcessorSettings
from app.processors.custom_processors.sp_setting_language import StateProcessorSettingsLanguage
from app.processors.custom_processors.sp_labor_cost_report import (
    StateProcessorLaborCostReport,
    StateProcessorLaborCostReportInProgress,
    StateProcessorLaborCostReportReady,
    StateProcessorLaborCostReportFilters,
    StateProcessorLaborCostReportFilterPeriod,
    StateProcessorLaborCostReportFilterReset
)

 
class StateProcessorManager():

    def __init__(self, session) -> None:
        
        self._session               = session
        self._app_resources         = ResourceDefinition(self._session.user.language)
        self._processors_cache      = {}
        self._processors_definition = {}
        
        self._init_processors_definition()
        self._init_command_maps()

    def get_processor(self, session, state_id: processorsTypes) -> StateProcessor:
        state_id_to_create = state_id

        if(self._processors_cache.get(state_id_to_create)):
            return self._processors_cache[state_id_to_create]

        if(state_id_to_create is None):
            state_id_to_create = processorsTypes.NONE

        processor = None
        processor_definition = self._processors_definition.get(state_id_to_create)

        if(processor_definition is None):
            processor_definition = self._processors_definition.get(processorsTypes.NOT_IMPLEMENTED)

        processor = processor_definition['cls'](session, processor_definition['chain'])

        return processor
   
    def get_processor_of_command(self, session, command_name):
        
        processor_id = self._command_map.get(command_name)
        assert processor_id is not None, f'Unsupported command "{command_name}"'
        processor = self.get_processor(session, processor_id)
        return processor

    def _init_command_maps(self):

        app_resources = ResourceDefinition() 

        self._command_map = {
            app_resources.command_start: processorsTypes.COMMAND_START,
            app_resources.command_admin: processorsTypes.COMMAND_ADMIN,
        }

    def _init_processors_definition(self):

        self._register_command_start_handler()
        self._register_command_admin_handler()
        self._register_none_handler()
        self._register_login_enter_email_handler()
        self._register_main_handler()
        self._register_not_implemented_handler()

    @staticmethod
    def _create_processor_definition(cls, chains):

        result_chains = {}

        for chain_key, chain_val in chains.items():
            
            if isinstance(chain_key, tgButton):
                result_chains[chain_key.action_id] = chain_val
                result_chains[chain_key.caption]   = chain_val
            else:
                result_chains[chain_key] = chain_val

        return {'cls': cls, 'chain': result_chains}
    
    def _register_command_start_handler(self):
        self._processors_definition[processorsTypes.COMMAND_START] =\
            self._create_processor_definition(
                StateProcessorCommandStart, 
                {
                    'NEXT': processorsTypes.NONE,
                }
            )
        
    def _register_command_admin_handler(self):
        self._processors_definition[processorsTypes.COMMAND_ADMIN] =\
            self._create_processor_definition(
                StateProcessorCommandAdmin, 
                {
                    'NEXT': processorsTypes.SET_ADMIN,
                }
            )
        self._register_set_admin_handler()
        
    def _register_set_admin_handler(self):

        self._processors_definition[processorsTypes.SET_ADMIN] =\
            self._create_processor_definition(
                    StateProcessorSetAdmin, 
                    {
                        'NEXT':processorsTypes.NONE
                    }
                )

    def _register_main_handler(self):
        app_resources = self._app_resources

        self._processors_definition[processorsTypes.MAIN] =\
             self._create_processor_definition(
                StateProcessorMainMenu, 
                {
                    app_resources.btnLaborCostReport:processorsTypes.LABOR_COST_REPORT,
                    app_resources.btnSettings  : processorsTypes.SETTINGS,
                    app_resources.btnHelp      : processorsTypes.HELP,
                }
            )
        
        self._register_labor_cost_report_handler()
        self._register_settings_handler()
        self._register_help_handler()

    def _register_labor_cost_report_handler(self):
        app_resources = self._app_resources

        self._processors_definition[processorsTypes.LABOR_COST_REPORT] =\
              self._create_processor_definition(
                    StateProcessorLaborCostReport, 
                    {
                     app_resources.btnFilters: processorsTypes.LABOR_COST_REPORT_FILTERS
                    }
            )
        
        self._processors_definition[processorsTypes.LABOR_COST_REPORT_INPROGRESS] =\
              self._create_processor_definition(
                    StateProcessorLaborCostReportInProgress, 
                    {}
            )
        
        self._processors_definition[processorsTypes.LABOR_COST_REPORT_READY] =\
              self._create_processor_definition(
                    StateProcessorLaborCostReportReady, 
                    {
                     app_resources.btnLaborCostReport: processorsTypes.LABOR_COST_REPORT,
                     app_resources.btnMainMenu: processorsTypes.MAIN,
                    }
            )
        
        self._register_lcr_filter_handler()
        
    def _register_lcr_filter_handler(self):
        app_resources = self._app_resources

        self._processors_definition[processorsTypes.LABOR_COST_REPORT_FILTERS] =\
              self._create_processor_definition(
                StateProcessorLaborCostReportFilters, 
                {
                    app_resources.btnFilterDate: processorsTypes.LABOR_COST_REPORT_FILTER_PERIOD,
                    app_resources.btnFilterProject: processorsTypes.LABOR_COST_REPORT_FILTER_PROJECT,
                    app_resources.btnFilterEmployee: processorsTypes.LABOR_COST_REPORT_FILTER_EMPLOYEE,
                    app_resources.btnResetFilter : processorsTypes.LABOR_COST_REPORT_FILTER_RESET

                }
            )
        
        self._register_lcr_filter_period_handler()
        self._register_lcr_filter_project_handler()
        self._register_lcr_filter_employee_handler()
        self._register_lcr_filter_reset_handler()

    

    def _register_lcr_filter_reset_handler(self):
        self._processors_definition[processorsTypes.LABOR_COST_REPORT_FILTER_RESET] =\
              self._create_processor_definition(StateProcessorLaborCostReportFilterReset, {})

    def _register_lcr_filter_period_handler(self):
        self._processors_definition[processorsTypes.LABOR_COST_REPORT_FILTER_PERIOD] =\
              self._create_processor_definition(StateProcessorLaborCostReportFilterPeriod, {})

    def _register_lcr_filter_project_handler(self):
        self._processors_definition[processorsTypes.LABOR_COST_REPORT_FILTER_PROJECT] =\
              self._create_processor_definition(StateProcessorChooseProjectFilter, {})
    
    def _register_lcr_filter_employee_handler(self):
        self._processors_definition[processorsTypes.LABOR_COST_REPORT_FILTER_EMPLOYEE] =\
              self._create_processor_definition(StateProcessorChooseEmployeeFilter, {})


    def _register_profile_view_handler(self):
        self._processors_definition[processorsTypes.PROFILE_VIEW] =\
              self._create_processor_definition(StateProcessorProfileView, {})
        
    def _register_choose_user_handler(self):
        self._processors_definition[processorsTypes.CHOOSE_USER] =\
            self._create_processor_definition(
                    StateProcessorChooseUser,
                    {
                        'NEXT': processorsTypes.USER_MANAGE
                    }
            )
        
        self._register_profile_manage_handler()
        
    def _register_profile_manage_handler(self):
        app_resources = self._app_resources

        self._processors_definition[processorsTypes.USER_MANAGE] =\
            self._create_processor_definition(
                    StateProcessorUserManagementMenu,
                    {
                        app_resources.btnSetRole: processorsTypes.USER_MANAGE_SET_ROLES,
                        app_resources.btnSetManager: processorsTypes.CHOOSE_MANAGERS,
                        #app_resources.btnBlockUser: processorsTypes.USER_MANAGE,
                        'NONE': processorsTypes.NONE
                    }
            )
        
        self._register_set_role_handler()
        self._register_choose_managers_handler()
        
    
    def _register_set_role_handler(self):
        self._processors_definition[processorsTypes.USER_MANAGE_SET_ROLES] =\
              self._create_processor_definition(StateProcessorUserManagementSetRoles, {})
        
    def _register_choose_managers_handler(self):
        self._processors_definition[processorsTypes.CHOOSE_MANAGERS] =\
              self._create_processor_definition(StateProcessorChooseManager, {})

    def _register_help_handler(self):
        self._processors_definition[processorsTypes.HELP] =\
              self._create_processor_definition(State_processor_help, {})
        
    def _register_settings_handler(self):
        app_resources = self._app_resources

        self._processors_definition[processorsTypes.SETTINGS] =\
            self._create_processor_definition(
                StateProcessorSettings, 
                {   
                    app_resources.btnProfileViewMenu:processorsTypes.PROFILE_VIEW,
                    app_resources.btnManageUsersMenu:processorsTypes.CHOOSE_USER,
                    app_resources.btnSettingsLanguage:processorsTypes.SETTINGS_LANGUAGE,
                    
                }
            )
        
        self._register_profile_view_handler()
        self._register_choose_user_handler()
        self._register_settings_language_handler()
    
    def _register_settings_language_handler(self):
        self._processors_definition[processorsTypes.SETTINGS_LANGUAGE] =\
               self._create_processor_definition(
                    StateProcessorSettingsLanguage, 
                    {
                        'NEXT':processorsTypes.SETTINGS_LANGUAGE
                    }
               )
    
    def _register_not_implemented_handler(self):
        app_resources = self._app_resources

        self._processors_definition[processorsTypes.NOT_IMPLEMENTED] =\
            self._create_processor_definition(
                StateProcessorNotImplemented, 
                {
                    app_resources.btnMainMenu: processorsTypes.MAIN,
                }
            )

    def _register_none_handler(self):

        self._processors_definition[processorsTypes.NONE] =\
            self._create_processor_definition(
                    StateProcessorNone, 
                    {
                        'LOGIN_INPUT_EMAIL':processorsTypes.LOGIN_INPUT_EMAIL,
                        'AUTH_USER':processorsTypes.MAIN
                    }
                )
        
    def _register_login_enter_email_handler(self):

        self._processors_definition[processorsTypes.LOGIN_INPUT_EMAIL] =\
            self._create_processor_definition(
                    StateProcessorLoginEmail, 
                    {
                        'NEXT':processorsTypes.LOGIN_INPUT_FULL_NAME
                    }
                )
        
        self._register_login_enter_name_handler()
    
    def _register_login_enter_name_handler(self):

        self._processors_definition[processorsTypes.LOGIN_INPUT_FULL_NAME] =\
            self._create_processor_definition(
                    StateProcessorLoginFullName, 
                    {
                        'NEXT':processorsTypes.LOGIN_INPUT_PHONE
                    }
                )
        
        self._register_login_enter_phone_handler()
        
    def _register_login_enter_phone_handler(self):

        self._processors_definition[processorsTypes.LOGIN_INPUT_PHONE] =\
            self._create_processor_definition(
                    StateProcessorLoginPhone, 
                    {
                        'NEXT':processorsTypes.LOGIN_WAIT_CONFIRMATION
                    }
                )
        self._register_login_wait_confirmation_handler()
        
    def _register_login_wait_confirmation_handler(self):

        self._processors_definition[processorsTypes.LOGIN_WAIT_CONFIRMATION] =\
            self._create_processor_definition(
                    StateProcessorLoginWaitConfirmation, 
                    {
                        'NEXT':processorsTypes.LOGIN_WAIT_CONFIRMATION
                    }
                )
    







   