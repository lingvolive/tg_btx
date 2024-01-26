
import asyncio

from app.config.config import Config
from app.models.factories.domain_objects_factory import DomainClassFactory
from app.models.factories.enum_domain_objects import domainObjectTypes
from app.store.factories.storage_config_factory import DBConfigFactory
from app.store.factories.datamapper_factory import DatamapperFactory



async def amain():
    
    config = Config('env')
    db_config_factory = DBConfigFactory(url = config.db.db_conn_str)
    datamapper = DatamapperFactory(id='local').get()
    await datamapper.install()

    user= DomainClassFactory.create(
                domainObjectTypes.User, 
                {'user_data':{'id':234567} }
        )
    
    role_admin = DomainClassFactory.create(
        domainObjectTypes.Role, {'data':{'user_id':user.id, 'name':'admin'}}
    )

    role_user = DomainClassFactory.create(
        domainObjectTypes.Role, {'data':{'user_id':user.id, 'name':'user'}}
    )

    datamapper.add_dataobject(user)

    async with datamapper as dm:
        await dm.fill_instance_from_db(user)
        print(user.roles)

if __name__ == '__main__':

    asyncio.run(amain())