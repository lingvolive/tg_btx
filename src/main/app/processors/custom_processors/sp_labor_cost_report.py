
from datetime import datetime
from dateutil.relativedelta import relativedelta


from app.resources.enums import processorsTypes
from app.processors.state_processor import StateProcessor
from app.models.custom_models.session.user_settings_manager import UserSettingsManager
from app.processors.custom_processors.service.labor_cost_report import LaborCostReport
from app.processors.tasks.events_manager import EventsManager, eventTypes

from app.telegram_bot.bot_interface import (
    tgButton,
    tgInlineMenu
)
    
class StateProcessorLaborCostReport(StateProcessor):

    def __init__(self, session, chain: dict) -> None:
        super().__init__(session, chain, processorsTypes.LABOR_COST_REPORT)

        self._menu = self.definitions.mLaborCostReportMenu

    def get_resetting_settings(self):
        return {
                #'report_filter_month': None,
                #'report_filter_project': None,
                #'report_filter_employee': None,
                }

    async def pre_process(self):
        app_resources = self.definitions
        report = LaborCostReport(self.session, app_resources)
        report.set_default_settings()

        message_text = f'{await report.view()}'
        
        #    message_text = f'{message_text}\n\n*{app_resources.strInProgress}*'

        await self.session.message.send(message_text, self._menu)

        return self.id
    
    async def process(self):

        state_id = await self._default_inline_keyboard_handler(self._menu)

        if( not state_id == self.id ):
            return state_id

        if( not self.session.message.is_inline() or 
           not self._menu == self.session.message.get_menu_id()
        ):
            return state_id

        app_resources = self.definitions
        settings_manager = UserSettingsManager(self.session)
        
        if(app_resources.btnGenerateReport ==self.session.message.get_action_id()):
            
            report = LaborCostReport(self.session, app_resources)
            settings_manager.set_setting('report_progress', 'in_progress')

            task_params = {
                'user_id': self.session.user.id,
                'bot': self.session.message.bot,
                'message_id': self.session.message.message_id,
                'settings': report.settings
            }

            even_manager = EventsManager()
            await even_manager.notify(eventTypes.LABOR_COST_REPORT, task_params)
            
            return processorsTypes.LABOR_COST_REPORT_INPROGRESS
        
        return self.id

class StateProcessorLaborCostReportInProgress(StateProcessor):

    def __init__(self, session, chain: dict) -> None:
        super().__init__(session, chain, processorsTypes.LABOR_COST_REPORT_INPROGRESS)


    def get_resetting_settings(self):
        return {}

    async def pre_process(self):
        app_resources = self.definitions
        report = LaborCostReport(self.session, app_resources)
        report.set_default_settings()

        message_text = f'{await report.view()}\n\n*{app_resources.strInProgress}*'

        await self.session.message.send(message_text)

        return self.id
    
    async def process(self):
        return self.id
    
class StateProcessorLaborCostReportReady(StateProcessor):

    def __init__(self, session, chain: dict) -> None:
        super().__init__(session, chain, processorsTypes.LABOR_COST_REPORT_READY)

        self._menu = self.definitions.mLaborCostReportReadyMenu

    def get_resetting_settings(self):
        return {}

    async def pre_process(self):
        app_resources = self.definitions
        report = LaborCostReport(self.session, app_resources)
        report.set_default_settings()

        user_settings = UserSettingsManager(self.session)
        report_file = user_settings.get_setting('report_file')
        message_text = f'{await report.view()}\n\n'

        await self.session.message.send_file(report_file, message_text, self._menu)

        return self.id
    
    async def process(self):
        return await self._default_inline_keyboard_handler(self._menu)



class StateProcessorLaborCostReportFilters(StateProcessor):

    def __init__(self, session, chain: dict) -> None:
        super().__init__(session, chain, processorsTypes.LABOR_COST_REPORT_FILTERS)

        self._menu = self.definitions.mLaborCostReportFilterMenu

    def get_resetting_settings(self):
        return {}

    async def pre_process(self):
        app_resources = self.definitions
        
        report = LaborCostReport(self.session, app_resources)
        message_text = f'{await report.view()}\n\n{app_resources.strAvailableFilters}'

        await self.session.message.send(message_text, self._menu)

        return self.id
    
    async def process(self):
        return await self._default_inline_keyboard_handler(self._menu)


class StateProcessorLaborCostReportFilterPeriod(StateProcessor):

    COUNT_BUTTONS_PER_ROW  = 1
    COUNT_ROWS_PER_PAGE = 6

    def __init__(self, session, chain: dict) -> None:
        super().__init__(session, 
                         chain, processorsTypes.LABOR_COST_REPORT_FILTER_PERIOD)
        
        self._menu_id = 'FILTER_PERIOD'
        self._action_id = 'CHOOSE_PERIOD'
        self._paging_action_id = 'PAGING_DATE'
        self._action_caption = self.definitions.strDateFilter

    def get_resetting_settings(self):
        return {
                'lcr_filter_period_page': 0,
                }
    
    async def pre_process(self):

        count_buttons = self.COUNT_BUTTONS_PER_ROW * self.COUNT_ROWS_PER_PAGE

        settings_manager = UserSettingsManager(self.session)
        page  = settings_manager.get_setting('lcr_filter_date_index', 0)

        date_index = page * count_buttons
        date_today = datetime.today()
        date_today = datetime(date_today.year, date_today.month, 1)
        
        buttons = {}
        row_index   = 0
        buttons.setdefault(row_index, [])

        for idx in range( count_buttons ):

            date = date_today - relativedelta( months=date_index)
            
            button = tgButton(
                date.strftime("%Y-%m"), 
                self._action_id, 
                date_index
            )

            if(date == date_today):
                button.set_default()

            if( len(buttons[row_index]) >= self.COUNT_BUTTONS_PER_ROW ):
                row_index += 1
                buttons.setdefault(row_index, [])
            
            buttons[row_index].append( button )
            date_index += 1
            
        menu = tgInlineMenu(self._menu_id)
        menu.set_buttons(buttons, 'inline' )
        buttons_prev = tgButton("<<", self._paging_action_id, page + 1)
        buttons_next = tgButton(">>", self._paging_action_id, page - 1)
        menu.add_row_of_buttons([buttons_prev, buttons_next])
        menu.add_row_of_buttons([self._definitions.btnBack])

        report = LaborCostReport(self.session, self.definitions)
        message_text = f'{await report.view()}\n\n*{self.definitions.strDateFilter}*'

        await self.session.message.send(message_text, menu)

        return self.id
    
    async def process(self):

        state_id =  await self._default_inline_keyboard_handler()

        if( not state_id == self.id ):
            return state_id

        if( not self.session.message.is_inline() or 
           not self._menu_id == self.session.message.get_menu_id()
        ):
            return state_id

        settings_manager = UserSettingsManager(self.session)
                
        if(self._paging_action_id == self.session.message.get_action_id() ):
            page = int(self.session.message.get_action_data())

            settings_manager.set_setting('lcr_filter_date_index', page)

            return self.id
        
        if(self._action_id ==self.session.message.get_action_id() ):
            report = LaborCostReport(self.session, self.definitions)
            date_index = int( self.session.message.get_action_data() )
            date = report.get_str_of_date_by_index(date_index)

            settings_manager.set_setting('report_filter_month', date)

            return settings_manager.pop_last_state_from_history()
        
        return self.id
    
class StateProcessorLaborCostReportFilterReset(StateProcessor):

    def __init__(self, session, chain: dict) -> None:
        super().__init__(session, 
                         chain, processorsTypes.LABOR_COST_REPORT_FILTER_RESET)
        

    def get_resetting_settings(self):
        return {}
    
    async def pre_process(self):

        report = LaborCostReport(self.session, self.definitions)
        report.reset_filters()
        user_setting = UserSettingsManager(self.session)
        state_id = user_setting.pop_last_state_from_history()

        return state_id
    
    async def process(self):

        state_id =  await self._default_inline_keyboard_handler()

        
    
    