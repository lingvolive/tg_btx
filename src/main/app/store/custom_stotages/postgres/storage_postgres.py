import logging
import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

from app.store.storage import Storage
from app.store.scheme import Scheme

from app.store.filters.filter import (
    Filters,
    ConditionTypeEQ
)

from app.store.sorting.sorting import Sorting
from app.store.paging.paging import Paging
from app.store.custom_stotages.postgres.sorting_processor_alchemy import SortingProcessorSqlAlchemy

from app.store.custom_stotages.postgres.filter_processor_postgress import (
    FilterProcessorPostgres
)

log = logging.getLogger(__name__)
Base = declarative_base()

class AlchemyModelsStore():

    _scheme_cls = {}

    def __init__(self):
        pass

    def create_alchemy_model(self, scheme :Scheme):
        class_name = f'Scheme{scheme.name}SQLAlchemy'

        scheme_class = self._scheme_cls.get(class_name)
        if(scheme_class is not None):
            return scheme_class

        class_bases = (Base,)
        class_dict = {"__tablename__": scheme.table}

        for column_name, column_type in scheme.get_db_col_types().items():
            class_dict[column_name] = column_type

        self._scheme_cls[class_name] = type(class_name, class_bases, class_dict)
        
        return self._scheme_cls[class_name] 
    
    def create_alchemy_model_instance_from_dict(self, scheme_cls, record : dict):

        record_for_filling = {}

        for col, value in record.items():
            if hasattr(scheme_cls, col):
                record_for_filling[col] = value

        return scheme_cls(**record_for_filling)

class StoragePostgres(Storage):

    accessible_driver = ['postgresql+asyncpg', 'mssql+pymssql']

    def __init__(self, url:str) -> None:
        super().__init__(url)

        self._is_opened    = False
        self._session_cls  = None
        self._session      = None
        self._transaction  = None
        self._engine       = None
        self._db_classes   = AlchemyModelsStore()

    async def begin_tran(self):
        uid = uuid.uuid4()
        log.debug(f'DB_BEGIN_TRAN_START: uid={uid}')

        await self.open()
        
        if( self._session is not None ):
            return
        
        try:
            self._session     = self._session_cls()
            self._transaction = await self._session.begin()
            log.debug(f'DB_BEGIN_TRAN_FINISH: uid={uid}')
        except Exception as err:
            log.error(f'DB_BEGIN_TRAN_ERROR: uid={uid}; err={err}')

    async def commit(self):
        uid = uuid.uuid4()
        log.debug(f'DB_COMMIT_TRAN_START: uid={uid}')
        if(self._transaction is None):
            return
        
        try:
            await self._transaction.commit()
            await self._session.close()

            log.debug(f'DB_COMMIT_TRAN_FINISH: uid={uid}')
        except Exception as err:
            log.error(f'DB_COMMIT_TRAN_ERROR: uid={uid}; err={err}')

        self._transaction = None
        self._session     = None

    async def rollback(self):
        uid = uuid.uuid4()
        log.debug(f'DB_ROLLBACK_START: uid={uid}')

        await self._transaction.rollback()
        await self._session.close()
        self._transaction = None
        self._session     = None

        log.debug(f'DB_ROLLBACK_FINISH: uid={uid}')

    async def close(self) -> None:
        uid = uuid.uuid4()
        log.debug(f'DB_CLOSE_START: uid={uid}')
       
        if self._is_opened:
            await self._engine.dispose()
            self._is_opened = False
            
        self._transaction = None
        self._session     = None

        log.debug(f'DB_CLOSE_FINISH: uid={uid}')

    async def is_tran_opened(self):
        return self._transaction is not None
    
    async def _open_session(self):

        if await self.is_tran_opened():
            return self._session
        else:
            session = None

            try:
                session = self._session_cls()
            except Exception as err:
                log.error(f'OPEN_SESSION_ERROR: {err}')
                raise

        return session
    
    async def _close_session(self, session):
        if await self.is_tran_opened():
            return
        await session.close()

    async def count(self, scheme: Scheme, filters: Filters):
        uid = uuid.uuid4()
        log.debug(f'DB_GET_COUNT_OF_RECORDS_START:uid={uid};scheme={scheme};filters={filters}')   
        await self.open()

        model = self._db_classes.create_alchemy_model(scheme)
        filter_processor = FilterProcessorPostgres(params={'scheme': model})
        db_filters = filter_processor.process(filters)
        key_column = getattr(model, scheme.primary_key)
        count = 0

        stmt   = select(func.count(key_column))
        if(not filters.is_empty()):
            stmt = stmt.where(db_filters)

        session = await self._open_session()
        
        try:
            result = await session.execute(stmt)
            count = result.scalar_one()

            log.debug(f'DB_GET_COUNT_OF_RECORDS_FINISH:uid={uid}')

        except Exception as err:
            log.error(f'DB_GET_COUNT_OF_RECORDS_START_ERROR:uid={uid};err={err}')
            raise Exception 
        finally:
            await self._close_session(session)

        return count
    
    async def delete(self, scheme: Scheme, filters: Filters, params :dict = None) -> None:
        uid = uuid.uuid4()
        log.debug(f'DB_DELETE_ROW_START:uid={uid};scheme={scheme};filters={filters}')

        model = self._db_classes.create_alchemy_model(scheme)
        filter_processor = FilterProcessorPostgres(params={'scheme': model})
        db_filters = filter_processor.process(filters)
        
        try:
            stmt = delete(model).where(db_filters) 
            await self._session.execute(stmt)
            log.debug(f'DB_DELETE_ROW_FINISH:uid={uid}')

        except Exception as err:
            log.error(f'DELETE_ROW_ERROR:uid={uid};err={err}')


    async def drop_scheme(self, scheme, params : dict = None) -> None:
        pass

    async def flush(self) -> None:
        pass

    async def install(self, schemes: list, params : dict = None) -> None:
        log.debug(f'DB_CREATE_TABLES_START')   
        await self.open()

        scheme_classes = []
        for scheme in schemes:
            scheme_class = self._db_classes.create_alchemy_model(scheme)
            scheme_classes.append(scheme_class)

        try:
            
            async with self._engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

            log.debug(f'DB_CREATE_TABLES_FINISH')   

        except Exception as err:
                log.error(f'DB_CREATE_TABLES_ERROR:{err}')
                raise Exception 
    
    async def open(self, params : dict = None) -> bool:
        uid = uuid.uuid4()
        log.debug(f'DB_CONNECT_START:uid={uid}')

        if(self._is_opened):
            return self._is_opened
        
        try:
            #engine = create_async_engine(
            #database_url,
            #connect_args={"server_settings": {"tcp_keepalives_idle": "600"}},
            #)
            self._engine = create_async_engine(self._url)
            self._session_cls = sessionmaker(
                self._engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
            log.debug(f'DB_CONNECT_FINFISH:uid={uid}')
        except Exception as err:
            log.error(f'DB_CONNECT_ERROR:uid={uid};err={err}')
            raise Exception
        
        self._is_opened = True
        Base.metadata.bind = self._engine
        return self._is_opened
        
    async def read(self, scheme, filters: Filters,
                    sorting: Sorting = None, paging: Paging = None,
                    params : dict = None
    ) -> list[dict]:
        uid = uuid.uuid4()
        log.debug(f'DB_READ_START:uid={uid};scheme={scheme};filters={filters}')
        await self.open()
        model = self._db_classes.create_alchemy_model(scheme)
        filter_processor = FilterProcessorPostgres(params={'scheme': model})
        db_filters = filter_processor.process(filters)

        if(sorting is not None):
            sorting_processor = SortingProcessorSqlAlchemy(params = {'model':model})
            db_sorting = sorting_processor.process(sorting)

        stmt = select(model)
        if(not filters.is_empty()):
            stmt = stmt.where(db_filters)

        if(sorting is not None):
            stmt = stmt.order_by(*db_sorting)

        if(paging is not None):
            stmt = stmt.offset(paging.offset).limit(paging.page_size)

        session = await self._open_session()

        try:
            
            result = await session.execute(stmt)
            result = result.scalars().all()
            log.debug(f'DB_READ_FINISH:uid={uid}')
        except Exception as err:
            result = []
            log.error(f'READING_FROM_DB_ERROR:uid={uid};err={err}')
        finally:
            await self._close_session(session)
       
        db_cols = scheme.db_col_names()
        rows = []
        for db_row in result:
            row = {}

            for col in db_cols:
                row[col] = getattr(db_row, col, None)
            rows.append(row)

        return rows

    async def save(self, scheme : Scheme, db_record: dict, params : dict = None) -> None:
        uid = uuid.uuid4()
        log.debug(f'DB_WRITE_START:uid={uid};scheme={scheme};record={db_record}')
        await self.open()
        
        record_exists = False
        primary_key   = scheme.primary_key

        if(db_record[primary_key] is None):
            db_record[primary_key] = scheme.new_primary_key()
        else:
            record_exists = await self._does_record_exist(scheme, db_record)
        
        scheme_cls = self._db_classes.create_alchemy_model(scheme)
        scheme_db_instance = self._db_classes.create_alchemy_model_instance_from_dict(
            scheme_cls,
            db_record
        )

        if(record_exists):
            primary_field = getattr(scheme_cls, primary_key)
            filter = (primary_field == db_record[primary_key])

            fields_for_update = {field: value 
                                    for field, value in db_record.items()
                                    if not field == primary_key
            }

            stmt_update = update(scheme_cls)
            stmt_where  = stmt_update.where(filter) 
            stmt        = stmt_where.values(**fields_for_update)

            try:
                await self._session.execute(stmt)
                log.debug(f'DB_UPDATE_FINISH:uid={uid}')
            except Exception as err:
                log.error(f'DB_UPDATE_ERROR:uid={uid};err={err}')
        else:  
            try:  
                self._session.add(scheme_db_instance)
                log.debug(f'DB_WRITE_FINISH:uid={uid}')
            except Exception as err:
                log.error(f'DB_WRITE_ERROR:uid={uid};err={err}')
            
            
    async def _does_record_exist(self, scheme: Scheme, record: dict):

        filters = Filters()
        filters.new_filter(
            ConditionTypeEQ(),
            scheme.primary_key,
            record[scheme.primary_key]
        )
        rows = await self.read(scheme, filters)
        return len(rows) > 0


    





    