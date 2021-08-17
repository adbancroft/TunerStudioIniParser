from os import stat, stat_result
from typing import Tuple, Type
from lark import Transformer, v_args, Tree, Token
from lark.visitors import TransformerChain
from collections import defaultdict
import more_itertools
from .TsIniFile import *

class TsParseTreeTransformer(TransformerChain):

    def __init__(self):
        super().__init__(_TsIniTransformerPhase1() * _TsIniTransformerPhase2())

class _TsIniTransformerPhase2(Transformer):

    @staticmethod
    def _to_dict(items):
        names = set((item.key for item in items))
        if len(items)!=len(names): 
            raise KeyError('')
        return dict(((item.key, item) for item in items))

    def start(self, children):
        header_section = Section(name='Header', lines=[c for c in children if c and not isinstance(c, AbstractSection)])
        sections= [header_section] + [c for c in children if isinstance(c, AbstractSection) and not c.is_empty()]
        return TsIniFile(self.__class__._to_dict(sections))

    def hashdef(self, children):
        return HashDef(**dict(children))

    def kvp_line(self, children):
        return KeyValuePair(kvp_key=children[0][1], values = children[1:])

    def generic_section(self, children):
        return Section(name=children[0][1], lines=children[1:])

    def constants_section(self, children):
        return ConstantsSection(name = "Constants", 
            header_lines=[item for item in children if not isinstance(item, Page)], 
            dict_kvp = self.__class__._to_dict([item for item in children if isinstance(item, Page)]))

    def page(self, children):
        return Page(page_num=children[0][1], dict_kvp=self.__class__._to_dict(children[1:]))

    def pcvariables_section(self, children):
        return DictSection(name='PcVariables', dict_kvp=self.__class__._to_dict(children))

    def kvp_bits_line(self, children):
        return BitVariable(**dict(children))

    def kvp_scalar_line(self, children):
        return ScalarVariable(**dict(children))        

    def kvp_array_line(self, children):
        kvp = dict(children)
        if 'dim1d' in kvp:
            return Array1dVariable(**kvp)
        else:
            return Array2dVariable(**kvp)

    def kvp_string_line(self, children):
        return StringVariable(**dict(children)) 

    def context_help_section(self, children):
        return DictSection(name = 'SettingContextHelp',  dict_kvp=dict(children))

    def tableeditor_section(self, children):
        return DictSection(name = 'TableEditor',  dict_kvp=self._to_dict(children))
        
    def table(self, children):
        return Table(**dict(more_itertools.collapse(children, levels=1, base_type=tuple)))

    def curveeditor_section(self, children):
        return DictSection(name = 'CurveEditor',  dict_kvp=self._to_dict(children))

    def curve(self, children):
        line_labels = ('line_labels', [c[1] for c in children if c[0]=='line_label'])
        children = [c for c in children if c[0]!='line_label'] + [line_labels]
        return Curve(**dict(children))

    def axis_limits(self, children):
        return Axis(**dict(children))

    def axis_bin(self, children):
        return AxisBin(**dict(children))

    # Collapse these to tuples so we can use them in dictionary comprehensions
    @v_args(tree=True)
    def _to_tuple(self, tree):
        return (tree.data, tree.children[0] if len(tree.children)==1 else tree.children)

    xaxis_limits = _to_tuple
    yaxis_limits = _to_tuple
    xbins = _to_tuple
    ybins = _to_tuple
    zbins = _to_tuple

class _TsIniTransformerPhase1(Transformer):
    
    def __default_token__(self, token):
        if isinstance(token.value, str):
            return token.value.strip('"')
        return token.value

    # Hoist these rules to just their child
    def _hoist_children(self, children):
        return children[0] if len(children)==1 else children

    char_constant = _hoist_children
    floating_constant = _hoist_children
    binary_constant = _hoist_children
    decimal_int_constant = _hoist_children
    hex_constant = _hoist_children
    string_literal = _hoist_children
    string_value = _hoist_children
    number_field = _hoist_children
    identifier = _hoist_children
    help_line_key = _hoist_children
    label = _hoist_children
    help_line = _hoist_children
    table_header = _hoist_children

    # Collapse these to tuples so we can use them in dictionary comprehensions
    @v_args(tree=True)
    def _to_tuple(self, tree):
        return (tree.data, tree.children[0] if len(tree.children)==1 else tree.children)
    kvp_key = _to_tuple
    data_type = _to_tuple
    offset = _to_tuple
    units = _to_tuple
    scale = _to_tuple
    low = _to_tuple
    high = _to_tuple
    digits = _to_tuple
    translate = _to_tuple
    dim1d = _to_tuple
    encoding = _to_tuple
    length = _to_tuple
    table_id = _to_tuple
    map3d_id = _to_tuple
    title = _to_tuple
    page_num = _to_tuple
    grid_height = _to_tuple
    section_name = _to_tuple   
    symbol = _to_tuple
    defined_value = _to_tuple
    grid_orient = _to_tuple
    curve_id = _to_tuple
    curve_name = _to_tuple
    min = _to_tuple
    max = _to_tuple
    step = _to_tuple
    constant_ref = _to_tuple
    outputchannel = _to_tuple
    name = _to_tuple
    code_override = _to_tuple
    help_topic = _to_tuple
    name = _to_tuple
    size = _to_tuple
    gauge = _to_tuple
    line_label = _to_tuple
    bit_size = _to_tuple
    dim2d = _to_tuple

    @v_args(tree=True)
    def _to_list(self, tree):
        return (tree.data, tree.children)
    unknown_values = _to_list        
    columnlabels = _to_list
    xy_labels = _to_list
    updown_labels = _to_list