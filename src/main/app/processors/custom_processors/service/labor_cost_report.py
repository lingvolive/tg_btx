
import os
import gc


from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

from app.services.bitrix import BitrixReport
from app.processors.custom_processors.service.user_management import UserManagement
from app.models.custom_models.session.user_settings_manager import UserSettingsManager

class LaborCostReport():

    def __init__(self, session, app_resources, settings: dict = None) -> None:
       
        self._session = session
        self._app_resources = app_resources

        if(settings is None):
            self.update_settings()
        else:
            self._settings = settings

    @property
    def settings(self):
        return self._settings

    async def view(self):
        app_resources = self._app_resources

        filter_date     = self._settings.get('filter_month')
        filter_project  = self._settings.get('filter_project')
        filter_employee = self._settings.get('filter_employee')

        user_management = UserManagement(self._session.user)
        if(filter_project is not None):
            project = await user_management.read_project_by_id(filter_project)
            filter_project = project.view(app_resources)

        if(filter_employee is not None):
            employee = await user_management.read_bitrix_user_by_id(filter_employee)
            filter_employee = employee.view(app_resources)


        filter_date = self._get_empty_str(filter_date, is_date = True)
        filter_project = self._get_empty_str(filter_project)
        filter_employee = self._get_empty_str(filter_employee)

        text_view = []
        text_view.append(f'*{app_resources.strLaborCostReport}:*\n')
        text_view.append(f'{app_resources.strDate}: {filter_date}')
        text_view.append(f'{app_resources.strProjectCaption}: {filter_project}')
        text_view.append(f'{app_resources.strEmployeeCaption}: {filter_employee}')

        return '\n'.join(text_view)
    
    def reset_filters(self):

        user_settings   = UserSettingsManager(self._session)
        user_settings.set_setting('report_filter_month' , None)
        user_settings.set_setting('report_filter_project', None)
        user_settings.set_setting('report_filter_employee', None)

        self.set_default_settings()

    def set_default_settings(self):
        user_settings = UserSettingsManager(self._session)
        filter_date   = user_settings.get_setting('report_filter_month')

        if(filter_date is None or filter_date == ''):
            date = self.get_str_of_date_by_index(0)
            user_settings.set_setting('report_filter_month', date)

        if( not self._session.user.has_role('manager') ):
            user_settings.set_setting('report_filter_employee', self._session.user.manager_id)


        self.update_settings()

    def update_settings(self):

        user_settings   = UserSettingsManager(self._session)
        self._settings = {
                'filter_month'  : user_settings.get_setting('report_filter_month'),
                'filter_project': user_settings.get_setting('report_filter_project'),
                'filter_employee': user_settings.get_setting('report_filter_employee')
            }

    def get_str_of_date_by_index(self, date_index):

        date_today = datetime.today()
        date_today = datetime(date_today.year, date_today.month, 1)
        date = date_today - relativedelta( months=date_index)
        
        return date.strftime("%Y-%m-%dT%H:%M:%S")
    
    def get_date_from_str(self, date_str):
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    
    def get_fmt_date_from_str(self, date_str, fmt):

        date = self.get_date_from_str(date_str)
        return date.strftime(fmt)
    
    def add_month_to_date_str(self, date_str):

        date_obj = self.get_date_from_str(date_str)
        date_obj = date_obj + relativedelta( months=1) - relativedelta(seconds=1)

        return date_obj.strftime("%Y-%m-%dT%H:%M:%S") 

    def _get_empty_str(self, line, is_date = False):
        if(line is None or line == ''):
            return '-'
        
        if(is_date):
            datetime_obj = self.get_date_from_str(line)
            line = datetime_obj.strftime('%d-%m-%Y')
        
        return line
    
    async def generate_report(self):

        user_management = UserManagement(None)
        date_start = self._settings.get('filter_month')
        
        filters={
            'date_start': date_start,
            'date_end': self.add_month_to_date_str(date_start),
            'project_id': self._settings.get('filter_project') ,
            'employee_id': self._settings.get('filter_employee') 
        }

        parts_of_file_name = []
        parts_of_file_name.append('LaborCostReport_')
        date_filename = self.get_fmt_date_from_str(date_start, '%Y_%m')
        parts_of_file_name.append(date_filename)

        if(filters['project_id'] is not None and filters['project_id'] > 0):
            project = await user_management.read_project_by_id(filters['project_id'])
            parts_of_file_name.append(project.name)

        if(filters['employee_id'] is not None and filters['employee_id'] > 0):
            user_bitrix = await user_management.read_bitrix_user_by_id(filters['employee_id'])
            user_name = user_bitrix.view(self._app_resources)
            parts_of_file_name.append(user_name)

        file_name = '_'.join(parts_of_file_name)
        file_name = f'{file_name}.xlsx'

        btx = BitrixReport()
        
        report_data = await btx.report_labor_cost(filters)
        report_file = await self._save_report_to_exel(report_data, file_name)

        del report_data
        gc.collect()

        return report_file

    async def _save_report_to_exel(self, report_data, file_name):

        from app.config.config import Config
        config = Config()

        out_file = os.path.join(config.tg_bot.path_files, file_name)

        sheetname = 'report'
        max_col_len = 50

        with pd.ExcelWriter(out_file, engine='xlsxwriter') as writer:
            
            report_data.to_excel(writer, sheet_name=sheetname, index=False)
            worksheet = writer.sheets[sheetname]
            worksheet.freeze_panes(1,0)
            worksheet.autofilter(0,0, report_data.shape[0], report_data.shape[1]-1)

            format_wrap = writer.book.add_format({'text_wrap': True})

            for idx, col in enumerate(report_data):
                series = report_data[col]
                max_len = max(
                              ( series.astype(str).map(len).max(), 
                                len(str(series.name)) 
                              )
                            ) + 3 
                
                worksheet.set_column(idx, idx, min(max_len, max_col_len), format_wrap)

        return out_file
