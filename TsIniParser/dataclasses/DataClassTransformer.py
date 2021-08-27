
from TsIniParser import BaseTransformer, RollupRuleProcessor, ChildRuleProcessor
from .TypeFactory import dataclass_factory

class DataClassTransformer(BaseTransformer):
    def __init__(self):
        super().__init__(return_processor = RollupRuleProcessor(), child_processor = ChildRuleProcessor(factory=dataclass_factory, key_getter=lambda item:item.key))