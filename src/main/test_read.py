
import asyncio

from app.config.config import Config
from app.models.factories.domain_objects_factory import DomainClassFactory
from app.models.factories.enum_domain_objects import domainObjectTypes
from app.store.factories.storage_config_factory import DBConfigFactory
from app.store.factories.datamapper_factory import DatamapperFactory

from app.store.filters.filter import (
    Filters,
    ConditionTypeEQ
)

from app.store.sorting.sorting import Sorting
from app.store.paging.paging import Paging


async def amain():
    
    config = Config('env')
    db_config_factory = DBConfigFactory(url = config.db.db_conn_str)
    datamapper = DatamapperFactory(id='local').get()
    await datamapper.install()

    user= DomainClassFactory.create(
                domainObjectTypes.User, 
                {'id':234567}
        )
   
    filters = Filters()
    filters.new_filter(ConditionTypeEQ(), 'is_wait_confirmation', True)
    sorting = Sorting()
    sorting.new_sorting('id', 'asc')
    sorting.new_sorting('full_name_ext', 'asc')
    paging = Paging(2, 4)
    
    rows = await datamapper.read(user.get_scheme(),
                                  filters=filters, 
                                  sorting=sorting, 
                                  paging=paging 
    )
    print(rows)

    #datamapper.add_dataobject(user)

    #async with datamapper as dm:
    #    await dm.fill_instance_from_db(user)
    #    print(user.roles)

if __name__ == '__main__':

    asyncio.run(amain())