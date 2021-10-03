from typing import Dict, Any
from . import ts_ini_file


def kvp_array_line_factory(**kwargs: Dict[str, Any]):
    if 'dim1d' in kwargs:
        return ts_ini_file.Array1dVariable(**kwargs)
    return ts_ini_file.Array2dVariable(**kwargs)


# Type tag to type mapping
_RULE_TYPEMAP = {
        'kvp_bits_line': ts_ini_file.BitVariable,
        'kvp_scalar_line': ts_ini_file.ScalarVariable,
        'kvp_array_line': kvp_array_line_factory,
        'kvp_string_line': ts_ini_file.StringVariable,
        'kvp_line': ts_ini_file.KeyValuePair,
        'page': ts_ini_file.Page,
        'constants_section': ts_ini_file.ConstantsSection,
        'pcvariables_section': ts_ini_file.DictSection,
        'context_help_section': ts_ini_file.DictSection,
        'axis_bin': ts_ini_file.AxisBin,
        'table': ts_ini_file.Table,
        'tableeditor_section': ts_ini_file.DictSection,
        'axis_limits': ts_ini_file.Axis,
        'curve': ts_ini_file.Curve,
        'curveeditor_section': ts_ini_file.DictSection,
        'generic_section': ts_ini_file.Section,
        'start': ts_ini_file.TsIniFile,
        'bit_size': ts_ini_file.BitSize,
        'dim2d': ts_ini_file.MatrixDimensions,
        'curve_dimensions': ts_ini_file.MatrixDimensions,
    }


def dataclass_factory(type_tag: str, dict_data: Dict[str, Any]):

    """ A factory that converts a type marker and dictionary into
    a class instance"""

    return _RULE_TYPEMAP[type_tag](**dict_data)
