
from lark.visitors import Transformer, Discard
from .TypeFactory import dataclass_factory

class DataClassTransformer(Transformer):

    def __init__(self):
        self._factory = dataclass_factory
        self._symbols = {}

    # ATM we only have one rule that needs this transform
    def help_line(self, children):
        return children

    # ================== Generic rule processing =====================

    # Hoist all tokens into their parent node
    def __default_token__(self, token):
        if isinstance(token.value, str):
            return token.value.strip('"')
        return token.value

    def _transform_children(self, children):
        """We always inline variable references - they need to appear in the original
        position of the variable reference, not as a nested item
        
        This has to happen when processing the rule that contains the
        variable_ref - we need to embed the child item not the child list"""

        def collapse_variable_refs(children):
            def is_variable_ref(item):
                return isinstance(item, tuple) and item[0] == self._var_tag
            
            for c in children:
                if is_variable_ref(c):
                    for item in c[1]:
                        yield item
                else:
                    yield c

        return collapse_variable_refs(super()._transform_children(children))

    # ================== Typed rule processing =====================
    # Lot's of rules need the same transform, so drive the processing by
    # look up.

    _dict_from_child_types = [
        'sections',
        'pages',
        'page_lines',
        'variables',
        'tables',
        'curves',
    ]

    _convert_to_type = [
        'start',
        'context_help_section',
        'constants_section',
        'page',
        'pcvariables_section',
        'tableeditor_section',
        'table',
        'curveeditor_section',
        'axis_limits',
        'generic_section',
        'kvp_line',
        'kvp_scalar_line',
        'kvp_bits_line',
        'kvp_array_line',
        'kvp_string_line',
        'axis_bin',
        'curve',
    ]

    _hoist_only_child = [
        'table_id',
        'map3d_id',
        'title',
        'grid_height',
        'zbins',
        'curve_id',
        'curve_name',
        'xaxis_limits',
        'yaxis_limits',
        'line_label',
        'min',
        'max',
        'step',
        'label',
        'units',
        'scale',
        'translate',
        'low',
        'high',
        'digits',
        'offset',
        'dim1d',
        'data_type',
        'symbol',
        'xbins',
        'ybins',
        'help_topic',
        'constant_ref',
        'outputchannel',
        'unknown',
        'inline_expression',
        'code_override',
        'name_override',
        'type_kvp',
        'filter_field',
        'type_other',
        'number_field',
        'page_num',
        'string_literal',
        'name',
    ]    

    # Applies to all rules not explicitly processed
    def __default__(self, data, children, meta):
        if data in self.__class__._dict_from_child_types:
            return ('dict_data', [(i.key, i) for i in children])

        if data in self.__class__._convert_to_type:
            return self._to_type(data, children)

        if data in self.__class__._hoist_only_child:
            if len(children)>1:
                raise ValueError()
            return (data, children[0] if children else None)
            
        # Default rule action is to transform to a tuple
        # 
        # These will typically go on to be dictionary entries 
        return (data, children)

    def _to_type(self, data, children):
        def collapse_dups(children):
            dup_map = {}
            for key, value in children:
                if key in dup_map:
                    if not isinstance(dup_map[key], list):
                        dup_map[key] = [dup_map[key]]
                    dup_map[key].append(value)
                else:
                    dup_map[key] = value
            return dup_map

        return self._factory(data, collapse_dups(children))

    # ================== #define, $symbol handling =====================

    def hashdef(self, children):
        # Record a symbol - will over write any previous definition
        self._symbols[children[0][1]] = children[1:]
        raise Discard

    _var_tag = 'variable_ref'

    def variable_ref(self, children):
        # Process a variable reference by returning the symbol value
        key = children[0]
        if key in self._symbols:
            # This is inlined into the parent tree children by other code
            return (self.__class__._var_tag, self._symbols[key])
        raise Discard