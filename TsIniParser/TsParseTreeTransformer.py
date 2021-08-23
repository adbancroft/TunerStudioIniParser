from os import stat, stat_result
from typing import Tuple, Type
from lark import Transformer, v_args, Tree, Token
from lark.visitors import TransformerChain
from collections import defaultdict
import more_itertools
from .TsIniFile import *

class TsParseTreeTransformer(TransformerChain):

    def __init__(self):
        super().__init__(_TsIniTransformerPhase1())# * _TsIniTransformerPhase2())

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

    # def axis_limits(self, children):
    #     return Axis(**dict(children))

    # def axis_bin(self, children):
    #     return AxisBin(**dict(children))

    # # Collapse these to tuples so we can use them in dictionary comprehensions
    # @v_args(tree=True)
    # def _to_tuple(self, tree):
    #     return (tree.data, tree.children[0] if len(tree.children)==1 else tree.children)

    # xaxis_limits = _to_tuple
    # yaxis_limits = _to_tuple
    # xbins = _to_tuple
    # ybins = _to_tuple
    # zbins = _to_tuple

class key:
    def __init__(self, value):
        self.value = value

class _TsIniTransformerPhase1(Transformer):

    @staticmethod
    def _dict_from_tuples(items):
        names = set(item[0] for item in items)
        if len(items)!=len(names): 
            raise KeyError('')
        return dict(((item[0], item[1]) for item in items))    

    @staticmethod
    def _dict_from_types(items):
        def _dict_key(items):
            return more_itertools.first_true(items, default=None, pred=lambda t: isinstance(t[1], key))

        def _to_keyed_tuple(child_item):
            if isinstance(child_item, dict):
                key_item = more_itertools.first_true(child_item.items(), default=None, pred=lambda t: isinstance(t[1], key))
                child_item[key_item[0]] = key_item[1].value
                key_value = key_item[1].value                
            elif isinstance(child_item, tuple) and isinstance(child_item[1], dict):
                key_item = more_itertools.first_true(child_item[1].items(), default=None, pred=lambda t: isinstance(t[1], key))
                child_item[1][key_item[0]] = key_item[1].value
                key_value = key_item[1].value
            elif isinstance(child_item, tuple):
                index = next(i for i,v in enumerate(child_item[1]) if isinstance(v[1], key))
                child_item[1][index] = (child_item[1][index][0], child_item[1][index][1].value)
                key_value = child_item[1][index][1]
            elif isinstance(child_item, list):
                index = next(i for i,v in enumerate(child_item) if isinstance(v, key))
                child_item[index] = child_item[index].value
                key_value = child_item[index]

            return (key_value, child_item)

        return _TsIniTransformerPhase1._dict_from_tuples([_to_keyed_tuple(i) for i in items])

    # Hoist all tokens into their parent node
    def __default_token__(self, token):
        if isinstance(token.value, str):
            return token.value.strip('"')
        return token.value

    def transform_hoist_children(self, children):
        return self.__class__._hoist_children_tag
    def transform_tuple_only(self, children):
        return self.__class__._tuple_only_tag 
    def transform_dict_from_tuples(self, children):
        return self.__class__._dict_from_tuple_tag        
    def transform_dict_from_types(self, children):
        return self.__class__._dict_from_types_tag
    def transform_is_key(self, children):
        return self.__class__._is_key_tag
    def transform_hoist_only_child(self, children):
        return self.__class__._hoist_child_tag
        
    _hoist_children_tag = transform_hoist_children.__name__
    _tuple_only_tag = transform_tuple_only.__name__
    _dict_from_tuple_tag = transform_dict_from_tuples.__name__
    _dict_from_types_tag = transform_dict_from_types.__name__
    _is_key_tag = transform_is_key.__name__
    _hoist_child_tag = transform_hoist_only_child.__name__

    _transform_tags = [
        _hoist_children_tag,
        _tuple_only_tag,
        _hoist_child_tag,
        _dict_from_tuple_tag,
        _dict_from_types_tag,
    ]

    # Apply defaults based empty rules (which act as tags)
    def __default__(self, data, children, meta):       
        transform_tags = [c for c in children if c in self.__class__._transform_tags]
        children = [c for c in children if c not in transform_tags]

        if self.__class__._is_key_tag in children:
            children = [c for c in children if c!=self.__class__._is_key_tag]
            # Keys have to be singular
            if len(children)>1:
                raise ValueError()
            children[0] = key(children[0])

        # _dict_from_tuple_tag==dictionary from raw tuples (item[0]==key)
        if self.__class__._dict_from_tuple_tag in transform_tags:
            children = self.__class__._dict_from_tuples(children)

        # _dict_from_types_tag==dictionary from typed tuples (item[0]==type, so key is in item[1]), no tuple
        if self.__class__._dict_from_types_tag in transform_tags:
            children = self.__class__._dict_from_types(children)

        # _hoist_children_tag == Pass children up to parent
        if self.__class__._hoist_children_tag in transform_tags:
            return children

        # _tuple_only_tag == convert to tuple, with ONLY ONE child
        if self.__class__._tuple_only_tag in transform_tags:
            if len(children)>1:
                raise ValueError()
            return (data, children[0] if children else None)

        if self.__class__._hoist_child_tag in transform_tags:
            if len(children)>1:
                raise ValueError()
            return children[0] if children else None

        # Default - convert to a tuple, with the tree node type as item[0]
        return (data, children)      
    