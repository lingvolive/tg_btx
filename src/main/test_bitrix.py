
import asyncio

from app.config.config import Config
from app.models.factories.domain_objects_factory import DomainClassFactory
from app.models.factories.enum_domain_objects import domainObjectTypes
from app.store.factories.storage_config_factory import DBConfigFactory
from app.store.factories.datamapper_factory import DatamapperFactory


from app.config.config import Config
from app.processors.tasks.task_bitrix import TaskNotifyEventImportDataFromBitrix

async def amain():
    
    config = Config('env')
    db_config_factory = DBConfigFactory(url = config.db.db_conn_str)
     
    task = TaskNotifyEventImportDataFromBitrix(params={})
    await task.process(None)
    

if __name__ == '__main__':

    asyncio.run(amain())