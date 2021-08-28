
from typing import Callable, Any

class RollupRuleProcessor:
    """Handles transform rules related to how a rule is rolled up the tree to it'a parent"""

    _rule_action_map = {
        # Rule names - if these change in the grammar, they need to change here
        'transform_hoist_children'  : lambda data, children: children,
        'transform_to_tagged_tuple' : lambda data, children: (data, children),
        'transform_to_rulename'     : lambda data, children: data,
    }
    _action_tags = list(_rule_action_map.keys())
    _default_action = _rule_action_map['transform_to_tagged_tuple']

    def extract_action(self, children):
        return_action = [c for c in children if c in self.__class__._action_tags]

        if len(return_action)>1:
            raise ValueError()
        return (self.__class__._rule_action_map[return_action[0]] if return_action else self.__class__._default_action,
                [c for c in children if c not in self.__class__._action_tags])

class ChildRuleProcessor:
    """Handles processing of transform rules that apply to a rules children"""

    def __init__(self, factory:Callable[[str, dict], Any], key_getter:Callable[[Any], Any]):
        self._factory = factory
        self._key_getter = key_getter

    @staticmethod
    def _dict_from_tuples(items):
        names = set(item[0] for item in items)
        if len(items)!=len(names):
            raise KeyError('')
        return {item[0]:item[1] for item in items}

    def _dict_from_types(self, data, children):
        return self.__class__._dict_from_tuples([(self._key_getter(i), i) for i in children])

    def _collapse_dups(self, data, children):
        dup_map = {}
        for key, value in children:
            if key in dup_map:
                if not isinstance(dup_map[key], list):
                    dup_map[key] = [dup_map[key]]
                dup_map[key].append(value)
            else:
                dup_map[key] = value
        return dup_map.items()

    def _to_type(self, data, children):
        return self._factory(data, self.__class__._dict_from_tuples(children))

    def _tuple_only(self, data, children):
        if len(children)>1:
            raise ValueError()
        return children[0] if children else None

    _rule_action_map = {
        # Rule names - if these change in the grammar, they need to change here
        'transform_collapse_dups'  :_collapse_dups,
        'transform_dict_from_types':_dict_from_types,
        'transform_tuple_only'     :_tuple_only,
        'transform_type_from_dict' :_to_type,
    }
    _action_tags = list(_rule_action_map.keys())

    def extract_actions(self, children):
        processing_action_tags = [c for c in children if c in self.__class__._action_tags]
        return (processing_action_tags, [c for c in children if c not in self.__class__._action_tags])

    def apply_actions(self, data, children, action_tags):
        for action_tag in action_tags:
            children = self.__class__._rule_action_map[action_tag](self, data, children)
        return children
