from lark import Transformer
from lark.visitors import Discard
from .RuleProcessors import RollupRuleProcessor, ChildRuleProcessor

class DataClassTransformer(Transformer):
    """Transforms the raw INI Lark tree by processing transform directives
    embedded in the grammar (as empty rules)
    
    The effect of the transform directives is determined by the injected rule processors

    Default is to transform into a dataclass
    """

    def __init__(self, return_processor = RollupRuleProcessor(), child_processor = ChildRuleProcessor()):
        self._symbols = {}
        self._return_processsor = return_processor
        self._child_processor = child_processor

    # Hoist all tokens into their parent node
    def __default_token__(self, token):
        if isinstance(token.value, str):
            return token.value.strip('"')
        return token.value

    def _transform_children(self, children):
        def collapse_variable_refs(children):
            flat_list = []
            for c in children:
                if isinstance(c, tuple) and c[0]=='variable_ref':
                    flat_list = flat_list + c[1]
                else:
                    flat_list.append(c)
            return flat_list

        # We always inline variable references - they need to appear in the original
        # position of the variable reference, not as a nested item
        #
        # This has to happen when processing the rule that contains the
        # variable_ref - we need to embed the child item not the child list
        return collapse_variable_refs(super()._transform_children(children))

    def __default__(self, data, children, meta):

        # Base rule processing of root transform rule. We can't tag this
        # with itself in the grammar - it introduces a circular reference into the rule
        if data=='transform_to_rulename':
            return data

        # Extract processing actions from children
        child_action_tags, children = self._child_processor.extract_actions(children)
        rollup_action, children = self._return_processsor.extract_action(children)

        # Apply child processing actions
        children = self._child_processor.apply_actions(data, children, child_action_tags)

        return rollup_action(data, children)

    # ================== #define, $symbol handling =====================

    def hashdef(self, children):
        self._symbols[children[0][1]] = children[1:]
        raise Discard

    def variable_ref(self, children):
        key = children[0]
        if key in self._symbols:
            return ('variable_ref', self._symbols[key])
        raise Discard