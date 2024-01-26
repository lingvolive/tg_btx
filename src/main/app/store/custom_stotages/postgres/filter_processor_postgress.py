from sqlalchemy import and_, or_, not_, true
from app.store.filters.filter import Filter, Filters, FilterGroupTypeAND
from app.store.filters.filter_processor import FilterAdapter, FilterProcessor


class FilterAdapterPostgres(FilterAdapter):

    def __init__(self, params : dict):
        super().__init__(params)
        self._alchemy_scheme_instance = params['scheme']
    
    def _filter_eq(self, filter:Filter):
        attr = getattr(self._alchemy_scheme_instance, filter.field_name)
        return attr == filter.value
    
    def _filter_neq(self, filter:Filter):
        attr = getattr(self._alchemy_scheme_instance, filter.field_name)
        return not_( attr == filter.value )
    
    def _filter_gt(self, filter:Filter):
        attr = getattr(self._alchemy_scheme_instance, filter.field_name)
        return attr > filter.value
    
    def _filter_gte(self, filter:Filter):
        attr = getattr(self._alchemy_scheme_instance, filter.field_name)
        return attr >= filter.value
    
    def _filter_lt(self, filter:Filter):
        attr = getattr(self._alchemy_scheme_instance, filter.field_name)
        return attr < filter.value
    
    def _filter_lte(self, filter:Filter):
        attr = getattr(self._alchemy_scheme_instance, filter.field_name)
        return attr <= filter.value

    def _filter_in(self, filter:Filter):
        attr = getattr(self._alchemy_scheme_instance, filter.field_name)
        return attr.in_(filter.value)
    
    def _filter_like(self, filter:Filter):
        pass
    
    def _filter_vector_similarity(self, filter:Filter):
        return True


class FilterProcessorPostgres(FilterProcessor):

    def __init__(self, params : dict) -> None:
        super().__init__(params)
        self._params = params

    def process(self, filters: Filters):
        
        filter_query = self._build_query_for_filter(filters)
        return filter_query
    
    def _build_query_for_filter(self, filter):

        filter_adapter = FilterAdapterPostgres(self._params)
        res_filter    = None

        if(isinstance(filter, Filter)):
            res_filter = filter_adapter.build_query_for_filter(filter)
        elif(isinstance(filter, Filters)):
            filters_list   = filter.get_filters()
            filter_type    = filter.get_condition_type()

            if(len(filters_list) == 0):
                return res_filter
            
            filters = []
            for filter in filters_list:
                filters.append( self._build_query_for_filter(filter) )
            
            if(isinstance(filter_type, FilterGroupTypeAND)):
                res_filter = and_(true(), *filters)
            else:
                res_filter = or_(true(), *filters)

        return res_filter

   