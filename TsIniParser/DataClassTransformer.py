from typing import Callable, Any
from lark import Transformer
from lark.visitors import Discard

class DataClassTransformer(Transformer):
    
    def __init__(self, factory:Callable[[str, dict], Any]):
        self._factory = factory
        self._symbols = {}

    @staticmethod
    def _dict_from_tuples(items):
        names = set(item[0] for item in items)
        if len(items)!=len(names): 
            raise KeyError('')
        return dict(((item[0], item[1]) for item in items))    

    @staticmethod
    def _dict_from_types(items):
        return DataClassTransformer._dict_from_tuples([(i.key, i) for i in items])

    # Hoist all tokens into their parent node
    def __default_token__(self, token):
        if isinstance(token.value, str):
            return token.value.strip('"')
        return token.value

    def transform_hoist_children(self, children):
        return self.__class__._hoist_children_tag
    def transform_tuple_only(self, children):
        return self.__class__._tuple_only_tag 
    def transform_dict_from_types(self, children):
        return self.__class__._dict_from_types_tag
    def transform_type_from_dict(self, children):
        return self.__class__._to_type_tag
    def transform_collapse_dups(self, children):
        return self.__class__._collapse_dups_tag
        
    _hoist_children_tag = transform_hoist_children.__name__
    _tuple_only_tag = transform_tuple_only.__name__
    _dict_from_types_tag = transform_dict_from_types.__name__
    _to_type_tag = transform_type_from_dict.__name__
    _collapse_dups_tag = transform_collapse_dups.__name__

    _transform_tags = [
        _dict_from_types_tag,
        _collapse_dups_tag,
        _to_type_tag,
        _hoist_children_tag,
        _tuple_only_tag,
    ]

    @staticmethod
    def _collapse_variable_refs(children): 
        flat_list = []
        for c in children:
            if isinstance(c, tuple) and c[0]=='variable_ref':
                flat_list = flat_list + c[1]
            else:
                flat_list.append(c)
        return flat_list

    # Apply defaults based empty rules (which act as tags)
    def __default__(self, data, children, meta):       
        transform_tags = [c for c in children if c in self.__class__._transform_tags]
        children = self.__class__._collapse_variable_refs((c for c in children if c not in transform_tags))

        if self.__class__._collapse_dups_tag in transform_tags:
            dup_map = {}
            for key, value in children:
                if key in dup_map:
                    if not isinstance(dup_map[key], list):
                        dup_map[key] = [dup_map[key]]
                    dup_map[key].append(value)
                else:
                    dup_map[key] = value
            children = [(key, value) for key, value in dup_map.items()]

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

        # Convert to a dataclass based type
        if self.__class__._to_type_tag in transform_tags:
            return self._factory(data, self.__class__._dict_from_tuples(children))

        # Default - convert to a tuple, with the tree node type as item[0]
        return (data, children)      
    
    def hashdef(self, children):
        self._symbols[children[0][1]] = self.__class__._collapse_variable_refs(children[1:])
        raise Discard

    def variable_ref(self, children):
        key = children[0]
        if key in self._symbols:
            return ('variable_ref', self._symbols[key])
        raise Discard