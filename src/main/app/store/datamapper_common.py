
from typing import Union

from app.store.datamapper import Datamapper

from app.models.factories.dbobjects import DBObject
from app.store.scheme import Scheme
from app.models.factories.domain_objects_factory import DomainClassFactory
from app.config.config import Config
from app.store.filters.filter import Filters
from app.store.sorting.sorting import Sorting
from app.store.paging.paging import Paging

class DatamapperCommon(Datamapper):

    def __init__(self) -> None:
        
        super().__init__()
       
        config = Config()
        self.init_storage(config.db.db_conn_str)
  
    def init_storage():
        pass

    
    async def count(self, scheme, filters):
        return await self._storage.count(scheme, filters)

    async def delete_dataobjects_from_db(self):
        pass

    async def fill_instance_from_db(self, cls_instance: DBObject):

        row_exist_in_db    = True
        scheme    = cls_instance.get_scheme()
        db_record = scheme.extract_schema_from_instance(cls_instance)
        filters   = scheme.get_primary_key_values_pairs(db_record, is_save = False)
        
        rows = await self._read_from_db(scheme, filters)

        if len(rows) == 0:
            row_exist_in_db = False
            row = scheme.extract_schema_from_instance(cls_instance)
        else: 
            row = rows[0]

        nested_instances = await self._read_nested_attributes(cls_instance, row)
        result_row = {**row, **nested_instances}
        
        scheme.fill_instance(cls_instance, result_row)

        return row_exist_in_db
    
    async def read(
        self, 
        scheme : Scheme,
        filters: Filters = None, 
        sorting: Sorting = None, 
        paging: Paging = None, 
       
    ) -> Union[DBObject, list[DBObject]]:
        
        rows = await self._read_from_db(scheme, filters = filters, 
                                        sorting = sorting, paging = paging)
        

        return await self._create_instance_from_rows(scheme, rows)

    async def write_dataobjects_to_db(self):

        await self._storage.open()
        await self._storage.begin_tran()

        try:
            for cls_instance in self._dataobjects:
                await self._save_instance(cls_instance, None, None)
        except Exception as err:
            await self._storage.rollback()
            
        await self._storage.commit()
        await self._storage.flush()
        await self._storage.close()

    async def _read_from_db( self, scheme: Scheme,
                            filters: Filters = None, sorting: Sorting = None, 
                            paging: Paging = None, ) -> list:

         return await self._storage.read(scheme, filters=filters, 
                                         sorting=sorting, paging = paging)
    
    async def _save_instance(
            self, 
            cls_instance : Union[ DBObject, list], 
            owner,
            owner_attribute
        ) -> None:

        if( isinstance(cls_instance, list) ):
            await self._save_list_of_instance(
                cls_instance, 
                owner, 
                owner_attribute
            )
            return

        
        if not cls_instance.is_modified():
            return

        scheme = cls_instance.get_scheme()
        db_record = scheme.extract_schema_from_instance(cls_instance, owner)
            
        await self._storage.save(scheme, db_record)
        setattr(cls_instance, scheme.primary_key, db_record[scheme.primary_key] )
        cls_instance.reset_modified()

        await self._save_nested_instance(cls_instance)

    async def _save_nested_instance(self, cls_instance : DBObject) -> None:

        scheme = cls_instance.get_scheme()
        nested_obj_attributes = scheme.get_nested_object_attributes()

        for attr, attr_properties in nested_obj_attributes.items():
            slave_instance = getattr(cls_instance, attr)

            if(slave_instance is None):
                continue
            
            await self._save_instance(
                slave_instance, 
                owner = cls_instance,
                owner_attribute = attr
            )

    async def _save_list_of_instance(
            self,
            cls_instance : Union[ DBObject, list], 
            owner : DBObject,
            owner_attribute : str
        ) -> None:

        if( not isinstance(cls_instance, list) ):
            return 

        if( owner is not None ):
            scheme_owner    = owner.get_scheme() 
            record_owner    = scheme_owner.extract_schema_from_instance(owner)
            record = scheme_owner.extract_nested_key_row(
                owner_attribute, 
                record_owner
            )
            scheme = scheme_owner.get_nested_scheme_by_attribute(owner_attribute)
            filters = scheme.get_primary_key_values_pairs(record, False)
            await self._storage.delete(scheme, filters)

        for item_cls_instance in cls_instance:
            item_cls_instance.modified()
            await self._save_instance(item_cls_instance, owner, owner_attribute)
    
    async def _fill_list_of_instance_from_db(self, cls_instances : list ):

        result = []

        for cls_instance in cls_instances:
            result.append( await self.fill_instance_from_db(cls_instance) )

        return result

    async def _fill_instance_from_list_of_rows(
            self, 
            nested_instance : list, 
            nested_scheme : Scheme, 
            nested_row :dict) -> list:

        if( len(nested_instance) > 0 ):
            await self._fill_list_of_instance_from_db(nested_instance)
        else:

            filters = nested_scheme.get_primary_key_values_pairs(nested_row, False)
            rows    = await self._read_from_db(nested_scheme, filters)

            nested_instance = await self._create_instance_from_rows(
                nested_scheme, 
                rows
            )

        return nested_instance
    
    async def _create_instance_from_rows(self, scheme: Scheme, rows: dict):

        instances = []

        for row in rows:
            instance = DomainClassFactory.create_from_scheme(scheme, {})
            nested_instances = await self._read_nested_attributes(instance, row)
            result_row = {**row, **nested_instances}
        
            scheme.fill_instance(instance, result_row)
            instances.append(instance)

        return instances

    async def _read_nested_attributes(self, cls_instance : DBObject, db_row):

        scheme = cls_instance.get_scheme()
        nested_obj_attributes = scheme.get_nested_object_attributes()
        nested_instances = {}

        for attr, attr_properties in nested_obj_attributes.items():

            nested_scheme  = attr_properties['scheme']
            nested_row     = scheme.extract_nested_key_row(attr, db_row)
            attr_value     = getattr(cls_instance, attr)

            if( attr_value is None ):
                nested_instance = DomainClassFactory.create_from_scheme(
                    nested_scheme,
                    nested_row)
            else:
                nested_instance = attr_value

            if isinstance(nested_instance, list) :
                nested_instance = await self._fill_instance_from_list_of_rows(
                                            nested_instance, 
                                            nested_scheme, 
                                            nested_row
                                        )
            else:
                await self.fill_instance_from_db(nested_instance)

            nested_instances[attr] = nested_instance

        return nested_instances

    

  
       