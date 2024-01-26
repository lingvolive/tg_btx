
from app.fast_bitrix24 import Bitrix, BitrixAsync
from app.config.config import Config

import pandas as pd
from app.resources.resource_definitions import ResourceDefinition 

class BitrixReport():

    def __init__(self) -> None:

        config = Config()
        self._url = config.btx.url_api_batch
        self._btx  = BitrixAsync(self._url, verbose=False)
        
    async def project_list(self):


        task_elapsed = self._btx.get_all_with_batch( 
                                'sonet_group.get',
                                params={
                                        'ORDER':{'NAME':'ASC'}
                                        } 
        )

        result = await task_elapsed
        return result

    async def report_labor_cost(self, filters):

        ds_columns = [u'TASK_ID', 'TASK_TITLE', 'USER', 'CREATED_DATE', 'TIME_HOUR', 'GROUP_NAME' ]
        start_date = filters['date_start']
        end_date   = filters['date_end']
        project_id = filters['project_id']
        user_id    = filters['employee_id']

        filters = {'>=CREATED_DATE': start_date, '<CREATED_DATE': end_date}

        if(user_id is not None):
            filters['USER_ID'] = user_id

        task_elepsed = self._btx.get_all_with_batch(
                                'task.elapseditem.getlist',
                                params={
                                'FILTER': filters,
                                        #'SELECT':['ID']
                                        } 
        )

        res = await task_elepsed

        if(len( res ) == 0):
            return pd.DataFrame([], columns=ds_columns) 

        dataset = pd.DataFrame(res)

        fileds = [ 
            {'new_colmn': 'TASK_TITLE', 'id_colmn':'TASK_ID', 'table_colmn':'TITLE'},
            {'new_colmn': 'GROUP_ID', 'id_colmn':'TASK_ID', 'table_colmn':'GROUP_ID'}
        ]
        await self.fill_filed(dataset, 'task.item.list', 'TASK_ID', fileds)

        if(project_id is not None):
                dataset = dataset[ dataset['GROUP_ID'] == f'{project_id}' ]

        fileds = [ { 'new_colmn': 'GROUP_NAME', 'id_colmn':'GROUP_ID', 'table_colmn':'NAME' } ]
        await self.fill_filed(dataset, 'sonet_group.get', 'GROUP_ID', fileds)

        fileds = [ { 'new_colmn': 'USER', 'id_colmn':'USER_ID', 'table_colmn':'LAST_NAME' } ]
        await self.fill_filed(dataset, 'user.get', 'USER_ID', fileds)

        dataset['SECONDS']= dataset['SECONDS'].astype(int)
        dataset['TIME_HOUR'] = (dataset['SECONDS'] / 3600).round(2)

        dataset['CREATED_DATE'] = pd.to_datetime(dataset['CREATED_DATE']).dt.date

        dataset['TASK_ID'] = dataset['TASK_ID'].astype(int)
        dataset.sort_values(by=['TASK_ID', 'CREATED_DATE'], inplace=True, ascending=True)

        dataset['CREATED_DATE'] = pd.to_datetime(dataset['CREATED_DATE']).dt.strftime('%d.%m.%Y')
        
        if(len(dataset) == 0):
            return pd.DataFrame([], columns=ds_columns) 

        return dataset[ ds_columns ]


    async def fill_filed(self, dataset, method, column_id_filter, fields):

        ids = dataset[ column_id_filter ].value_counts().index

        if len(ids) == 0:
            return

        task = self._btx.get_by_ID( method, list(ids), 'FILTER[ID]', params={'order':{'ID':'ASC'}} )

        result = await task
        table = dict( [ ( result_item['ID'], result_item ) for result_item in result ] )

        for field_item in fields:

            dataset[ field_item['new_colmn'] ] = \
                dataset[ field_item['id_colmn'] ].apply(lambda x: table[x][ field_item['table_colmn'] ] if table.get(x) != None else '')
