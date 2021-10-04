from typing import Iterable, Tuple, Any
from . import ts_ini_file


def kvp_array_line_factory(children):
    children = dict(children)
    if 'dim1d' in children:
        return ts_ini_file.Array1dVariable(**children)
    return ts_ini_file.Array2dVariable(**children)


def dedup_factory(type, children):
    def _collapse_dups(children):
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

    children = _collapse_dups(children)
    return type(**children)


def generic_factory(type, children):
    return type(**dict(children))


# Type tag to type mapping
_RULE_TYPEMAP = {
        'kvp_bits_line': lambda children: generic_factory(ts_ini_file.BitVariable, children),
        'kvp_scalar_line': lambda children: generic_factory(ts_ini_file.ScalarVariable, children),
        'kvp_array_line': kvp_array_line_factory,
        'kvp_string_line': lambda children: generic_factory(ts_ini_file.StringVariable, children),
        'kvp_line': lambda children: generic_factory(ts_ini_file.KeyValuePair, children),
        'page': lambda children: generic_factory(ts_ini_file.Page, children),
        'constants_section': lambda children: generic_factory(ts_ini_file.ConstantsSection, children),
        'pcvariables_section': lambda children: generic_factory(ts_ini_file.DictSection, children),
        'context_help_section': lambda children: generic_factory(ts_ini_file.DictSection, children),
        'axis_bin': lambda children: generic_factory(ts_ini_file.AxisBin, children),
        'table': lambda children: generic_factory(ts_ini_file.Table, children),
        'tableeditor_section': lambda children: generic_factory(ts_ini_file.DictSection, children),
        'axis_limits': lambda children: generic_factory(ts_ini_file.Axis, children),
        'curve': lambda children: dedup_factory(ts_ini_file.Curve, children),
        'curveeditor_section': lambda children: generic_factory(ts_ini_file.DictSection, children),
        'generic_section': lambda children: generic_factory(ts_ini_file.Section, children),
        'start': lambda children: generic_factory(ts_ini_file.TsIniFile, children),
        'bit_size': lambda children: generic_factory(ts_ini_file.BitSize, children),
        'dim2d': lambda children: generic_factory(ts_ini_file.MatrixDimensions, children),
        'curve_dimensions': lambda children: generic_factory(ts_ini_file.MatrixDimensions, children),
    }


def dataclass_factory(type_tag: str, children: Iterable[Tuple[str, Any]]):

    """ A factory that converts a type marker and dictionary into
    a class instance"""

    return _RULE_TYPEMAP[type_tag](children)
