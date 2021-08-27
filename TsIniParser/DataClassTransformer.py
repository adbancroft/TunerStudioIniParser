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
    
    def _dict_from_types(self, data, children):
        return self.__class__._dict_from_tuples([(i.key, i) for i in children])

    def _collapse_dups(self, data, children):
        dup_map = {}
        for key, value in children:
            if key in dup_map:
                if not isinstance(dup_map[key], list):
                    dup_map[key] = [dup_map[key]]
                dup_map[key].append(value)
            else:
                dup_map[key] = value
        return [(key, value) for key, value in dup_map.items()]

    def _to_type(self, data, children):
        return self._factory(data, self.__class__._dict_from_tuples(children))

    def _tuple_only(self, data, children):
        if len(children)>1:
            raise ValueError()
        return (data, children[0] if children else None)  

    # Hoist all tokens into their parent node
    def __default_token__(self, token):
        if isinstance(token.value, str):
            return token.value.strip('"')
        return token.value
       
    _hoist_children_tag = 'transform_hoist_children'
    _tuple_only_tag = 'transform_tuple_only'
    _dict_from_types_tag = 'transform_dict_from_types'
    _to_type_tag = 'transform_type_from_dict'
    _collapse_dups_tag = 'transform_collapse_dups'
    _to_tagged_tuple_tag = 'transform_to_tagged_tuple'

    _child_processing_actions = {
        _collapse_dups_tag:_collapse_dups,
        _dict_from_types_tag:_dict_from_types,
        _tuple_only_tag:_tuple_only,
        _to_type_tag:_to_type,
    }
    _child_processing_tags = list(_child_processing_actions.keys())

    _return_actions = {
        _hoist_children_tag: lambda data, children: children,
        _to_tagged_tuple_tag : lambda data, children: (data, children)
    }
    _return_action_tags = list(_return_actions.keys())
    _default_return_action = _return_actions[_to_tagged_tuple_tag]

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
        # Base rule processing of root transform tag rule
        if data=='transform_to_rulename' or 'transform_to_rulename' in children:
            return data

        processing_action_tags = [c for c in children if c in self.__class__._child_processing_tags]
        return_action = [c for c in children if c in self.__class__._return_action_tags]
        children = self.__class__._collapse_variable_refs((c for c in children if c not in processing_action_tags and c not in return_action))
        
        for action_tag in processing_action_tags:
            children = self.__class__._child_processing_actions[action_tag](self, data, children)

        if len(return_action)>1:
            raise ValueError()
        return_action = self.__class__._return_actions[return_action[0]] if return_action else self.__class__._default_return_action
        return return_action(data, children)

    # ================== #define, $symbol handling =====================

    def hashdef(self, children):
        self._symbols[children[0][1]] = self.__class__._collapse_variable_refs(children[1:])
        raise Discard

    def variable_ref(self, children):
        key = children[0]
        if key in self._symbols:
            return ('variable_ref', self._symbols[key])
        raise Discard