
from app.processors.tasks.task import Task
from app.fast_bitrix24 import Bitrix, BitrixAsync
from app.config.config import Config
from app.models.factories.enum_domain_objects import domainObjectTypes
from app.models.factories.domain_objects_factory import DomainClassFactory
from app.store.factories.datamapper_factory import DatamapperFactory

class TaskNotifyEventImportDataFromBitrix(Task):

    def __init__(self, params: dict) -> None:
        super().__init__(params)
        #self._user_id = params['user_id']
        #self._bot = params['bot']

    async def _process_import_users(self, btx, datamapper, domain_factory):

        users = await btx.get_all_with_batch('user.get', params={})
        datamapper.reset_dataobjects()

        for user in users:

            user_bitrix = domain_factory.create(
                domainObjectTypes.UserBitrix,
                {
                    'id': int( user['ID']),
                    'name': user['NAME'],
                    'last_name': user['LAST_NAME'],
                    'email': user['EMAIL'],
                }
                                                
            )

            user_bitrix.modified()
            datamapper.add_dataobject(user_bitrix)
        
        await datamapper.write_dataobjects_to_db()

    async def _process_import_projects(self, btx, datamapper, domain_factory):

        projects = await btx.get_all_with_batch('sonet_group.get', params={})
        datamapper.reset_dataobjects()

        for btx_project in projects:
             
            project  = domain_factory.create(
                domainObjectTypes.Project,
                {
                    'id': int( btx_project['ID']),
                    'name': btx_project['NAME'],
                    'deleted': False
                }
            )
             
            project.modified()
            datamapper.add_dataobject(project)

        await datamapper.write_dataobjects_to_db()
             
        
    async def process(self, state_processor_manager_cls):

        config = Config()
        btx = BitrixAsync(config.btx.url_api_batch, verbose=False)
        datamapper = DatamapperFactory(id='local').get()
        domain_factory = DomainClassFactory()
        
        await datamapper.install()

        await self._process_import_users(btx, datamapper, domain_factory)
        await self._process_import_projects(btx, datamapper, domain_factory)

        return