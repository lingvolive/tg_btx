
from app.store.filters.filter import (
    Filters,
    Filter,
    ConditionTypeEQ,
    ConditionTypeNEQ,
    ConditionTypeGT,
    ConditionTypeGTE,
    ConditionTypeLT,
    ConditionTypeLTE,
    ConditionTypeIN,
    ConditionTypeLike,
    ConditionTypeVectorSimilarity,
    FilterGroupTypeAND,
    FilterGroupTypeOR,

)

class FilterAdapterCSV:

    def __init__(self):
        pass

    def build_query_for_filter(self, filter:Filter):

        if(isinstance(filter.filter_type, ConditionTypeEQ)):
            return self._filter_eq(filter)
        if(isinstance(filter.filter_type, ConditionTypeNEQ)):
            return self._filter_neq(filter)
        if(isinstance(filter.filter_type, ConditionTypeGT)):
            return self._filter_gt(filter)
        if(isinstance(filter.filter_type, ConditionTypeGTE)):
            return self._filter_gte(filter)
        if(isinstance(filter.filter_type, ConditionTypeLT)):
            return self._filter_lt(filter)
        if(isinstance(filter.filter_type, ConditionTypeLTE)):
            return self._filter_lte(filter)
        if(isinstance(filter.filter_type, ConditionTypeIN)):
            return self._filter_in(filter)
        if(isinstance(filter.filter_type, ConditionTypeLike)):
            return self._filter_like(filter)
        if(isinstance(filter.filter_type, ConditionTypeVectorSimilarity)):
            return self._filter_vector_similarity(filter)

    def _filter_eq(self, filter:Filter):
        symbol_quote = filter.symbol_quote()
        return f'{filter.field_name}=={symbol_quote}{filter.value}{symbol_quote}'

    def _filter_neq(self, filter:Filter):
        symbol_quote = filter.symbol_quote()
        return f'{filter.field_name}!={symbol_quote}{filter.value}{symbol_quote}'

    def _filter_gt(self, filter:Filter):
        symbol_quote = filter.symbol_quote()
        return f'{filter.field_name}>{symbol_quote}{filter.value}{symbol_quote}'

    def _filter_gte(self, filter:Filter):
        symbol_quote = filter.symbol_quote()
        return f'{filter.field_name}>={symbol_quote}{filter.value}{symbol_quote}'

    def _filter_lt(self, filter:Filter):
        symbol_quote = filter.symbol_quote()
        return f'{filter.field_name}<{symbol_quote}{filter.value}{symbol_quote}'

    def _filter_lte(self, filter:Filter):
        symbol_quote = filter.symbol_quote()
        return f'{filter.field_name}<={symbol_quote}{filter.value}{symbol_quote}'

    def _filter_in(self, filter:Filter):
        raise NotImplemented

    def _filter_like(self, filter:Filter):
        raise NotImplemented
    
    def _filter_vector_similarity(self, filter:Filter):
        raise NotImplemented

class FilterProcessorCSV():

    def __init__(self) -> None:
        pass

    def process(self, filters : Filters):
      
        return self._build_query_for_filter(filters)
        
    def _build_query_for_filter(self, filter):

        filter_adapter = FilterAdapterCSV()
        result_filters = []

        if(isinstance(filter, Filter)):
            return filter_adapter.build_query_for_filter(filter)
        else:
            filters_list   = filter.get_filters()
            filter_type    = filter.get_condition_type()

            if(len(filters_list) == 0):
                return ''
        
            filters = []
            for filter in filters_list:
                filters.append( self._build_query_for_filter(filter) )
            
            if(isinstance(filter_type, FilterGroupTypeAND)):
                loc_filter = '&'.join(filters)
            else:
                loc_filter = '|'.join(filters)
            
            return loc_filter

                 


