
from lark.visitors import Transformer, Discard, v_args
from .type_factory import dataclass_factory


class DataClassTransformer(Transformer):

    def __init__(self):
        super().__init__()
        self._factory = dataclass_factory
        self._symbols = {}

    # ================== Generic rule processing =====================

    # Hoist all tokens into their parent node
    def __default_token__(self, token):
        if isinstance(token.value, str):
            return token.value.strip('"')
        return token.value

    # ================== Typed rule processing =====================
    # Lot's of rules need the same transform, so drive the processing by
    # look up.

    def dict_from_child_types(self, children):
        return ('dict_data', [(i.key, i) for i in children])

    sections = dict_from_child_types
    pages = dict_from_child_types
    page_lines = dict_from_child_types
    variables = dict_from_child_types
    tables = dict_from_child_types
    curves = dict_from_child_types

    @v_args(tree=True)
    def convert_to_type(self, tree):
        return self._to_type(tree.data, tree.children)

    start = convert_to_type
    context_help_section = convert_to_type
    constants_section = convert_to_type
    page = convert_to_type
    pcvariables_section = convert_to_type
    tableeditor_section = convert_to_type
    table = convert_to_type
    curveeditor_section = convert_to_type
    axis_limits = convert_to_type
    generic_section = convert_to_type
    kvp_line = convert_to_type
    kvp_scalar_line = convert_to_type
    kvp_bits_line = convert_to_type
    kvp_array_line = convert_to_type
    kvp_string_line = convert_to_type
    axis_bin = convert_to_type
    curve = convert_to_type

    @v_args(tree=True)
    def to_tuple_and_type(self, tree):
        return (tree.data, self._to_type(tree.data, tree.children))

    bit_size = to_tuple_and_type
    dim2d = to_tuple_and_type
    curve_dimensions = to_tuple_and_type

    @v_args(tree=True)
    def hoist_only_child(self, tree):
        if len(tree.children) > 1:
            raise ValueError()
        return (tree.data, tree.children[0] if tree.children else None)

    table_id = hoist_only_child
    map3d_id = hoist_only_child
    title = hoist_only_child
    grid_height = hoist_only_child
    zbins = hoist_only_child
    curve_id = hoist_only_child
    curve_name = hoist_only_child
    line_label = hoist_only_child
    min = hoist_only_child
    max = hoist_only_child
    step = hoist_only_child
    label = hoist_only_child
    units = hoist_only_child
    scale = hoist_only_child
    translate = hoist_only_child
    low = hoist_only_child
    high = hoist_only_child
    digits = hoist_only_child
    offset = hoist_only_child
    dim1d = hoist_only_child
    type_name = hoist_only_child
    symbol = hoist_only_child
    table_xbin = hoist_only_child
    table_ybin = hoist_only_child
    help_topic = hoist_only_child
    variable = hoist_only_child
    outputchannel = hoist_only_child
    unknown = hoist_only_child
    inline_expression = hoist_only_child
    code_override = hoist_only_child
    name_override = hoist_only_child
    type_kvp = hoist_only_child
    filter_field = hoist_only_child
    type_other = hoist_only_child
    number_field = hoist_only_child
    page_num = hoist_only_child
    name = hoist_only_child
    start_bit = hoist_only_child
    bit_length = hoist_only_child
    xsize = hoist_only_child
    ysize = hoist_only_child
    curve_gauge = hoist_only_child

    def to_child(self, children):
        if len(children) != 1:
            raise ValueError()
        return children[0]

    string_literal = to_child

    def to_children(self, children):
        return children

    help_line = to_children

    # Applies to all rules not explicitly processed
    def __default__(self, data, children, meta):
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
                    for item in value:
                        dup_map[key].append(item)
                else:
                    dup_map[key] = value
            return dup_map

        return self._factory(data, collapse_dups(children))

    # ================== #define, $symbol handling =====================

    def hashdef_line(self, children):
        # Record a symbol - will over write any previous definition
        self._symbols[children[0][1]] = children[1:]
        raise Discard

    _var_tag = 'variable_ref'

    def variable_ref(self, children):
        if children[0] not in self._symbols:
            # Reference to non-existent variable.
            # Handle as if the variable ref never happened
            #
            # Equivalent of:
            #   #undef BREAD
            #   toast(BREAD)
            raise Discard
        return (self._var_tag, children[0])

    def _transform_children(self, children):
        """We always inline variable references - they need to appear in the original
        position of the variable reference, not as a nested item

        This has to happen when processing the rule that contains the
        variable_ref - we need to embed the child item not the child list"""

        def collapse_variable_refs(children):
            def is_variable_ref(item):
                return isinstance(item, tuple) and item[0] == self._var_tag

            for child in children:
                if is_variable_ref(child):
                    # Need to use yield from in case the variable contains multiple
                    # entries. We don't want a list in place of the variable, we want
                    # the list items inline. E.g.
                    #   #define BREAD_LIKE ciabatta, bagel
                    #   toast(BREAD_LIKE)
                    yield from self._symbols[child[1]]
                else:
                    yield child

        return collapse_variable_refs(super()._transform_children(children))
