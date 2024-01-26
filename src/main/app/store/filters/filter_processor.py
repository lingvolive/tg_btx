
from abc import ABC, abstractmethod

from app.store.filters.filter import (
    Filters,
    Filter,
    ConditionTypes,
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

class FilterAdapter:

    def __init__(self, params : dict):
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

    @abstractmethod
    def _filter_eq(self, filter:Filter):
        pass

    @abstractmethod
    def _filter_neq(self, filter:Filter):
        pass

    @abstractmethod
    def _filter_gt(self, filter:Filter):
        pass

    @abstractmethod
    def _filter_gte(self, filter:Filter):
        pass

    @abstractmethod
    def _filter_lt(self, filter:Filter):
        pass
    
    @abstractmethod
    def _filter_lte(self, filter:Filter):
        pass

    @abstractmethod
    def _filter_in(self, filter:Filter):
        pass

    @abstractmethod
    def _filter_like(self, filter:Filter):
        pass
    
    @abstractmethod
    def _filter_vector_similarity(self, filter:Filter):
        pass


class FilterProcessor(ABC):

    def __init__(self, params : dict) -> None:
        pass
    
    @abstractmethod
    def process(self, filters : Filters):
        pass

         

                 


