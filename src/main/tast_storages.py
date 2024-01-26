
import asyncio
import logging
import time

from app.config.config import Config
from app.models.factories.domain_objects_factory import DomainClassFactory
from app.models.factories.enum_domain_objects import domainObjectTypes
from app.store.factories.storage_config_factory import DBConfigFactory
from app.store.factories.datamapper_factory import DatamapperFactory

from app.store.custom_stotages.postgres.storage_postgres import StoragePostgres
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AsyncElasticsearch')

from concurrent.futures import ThreadPoolExecutor
task_queue = asyncio.Queue() 

async def task_processor():

    dm = DatamapperFactory(id='local')

    datamapper = DatamapperFactory().get()
   
    while True:
        task = await task_queue.get()
        if task is None:
            break

        datamapper.reset_dataobjects()
        datamapper.add_dataobject(task['user'])

        task_id = task['task_id']

        print(f'Current thread ID: {threading.current_thread().ident}-{task_id}')
        async with datamapper as dm:

            for idx in range(1):
                start = time.monotonic()
                await dm.fill_instance_from_db(task['user'])
                print(time.monotonic() - start)
            
            
    print(f'Exit thread ID: {threading.current_thread().ident}')

async def start_pool():

    executer = ThreadPoolExecutor(max_workers=5)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
            executer, 
            task_processor
    )     

async def amain():

    config = Config('env')
    db_config_factory = DBConfigFactory(url = config.db.db_conn_str)
    dm = DatamapperFactory(id='local').get()
    await dm.install()


    start = time.monotonic()
    
    tasks = [] 
    for _ in range(1):
        task = asyncio.create_task(task_processor())
        tasks.append(task)

    number_task = 1

    for idx in range(number_task):
        user= DomainClassFactory.create(
                domainObjectTypes.User, 
                {'user_data':{'id':234567 + idx}}
        )

        task = {
            'user':user,
            'task_id': idx
        }

        await task_queue.put(task)

    for idx in range(number_task):
        await task_queue.put(None)

    for task in tasks:
        await task

    print(time.monotonic() - start)

    return
    
if __name__ == '__main__':

    asyncio.run(amain())


