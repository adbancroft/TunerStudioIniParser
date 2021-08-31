from typing import Dict, Any
from . import TsIniFile


# Type tag to type mapping
_RULE_TYPEMAP = {
        'kvp_bits_line': TsIniFile.BitVariable,
        'kvp_scalar_line': TsIniFile.ScalarVariable,
        'kvp_array_line': TsIniFile.Array1dVariable,
        'kvp_string_line': TsIniFile.StringVariable,
        'kvp_line': TsIniFile.KeyValuePair,
        'page': TsIniFile.Page,
        'constants_section': TsIniFile.ConstantsSection,
        'pcvariables_section': TsIniFile.DictSection[TsIniFile.Variable],
        'context_help_section': TsIniFile.DictSection[str],
        'axis_bin': TsIniFile.AxisBin,
        'table': TsIniFile.Table,
        'tableeditor_section': TsIniFile.DictSection[TsIniFile.Table],
        'axis_limits': TsIniFile.Axis,
        'curve': TsIniFile.Curve,
        'curveeditor_section': TsIniFile.DictSection[TsIniFile.Curve],
        'generic_section': TsIniFile.Section,
        'start': TsIniFile.TsIniFile,
    }


def dataclass_factory(type_tag: str, dict_data: Dict[str, Any]):

    """ A factory that converts a type marker and dictionary into
    a class instance"""

    if type_tag == 'kvp_array_line':
        if 'dim1d' in dict_data:
            class_type = TsIniFile.Array1dVariable
        else:
            class_type = TsIniFile.Array2dVariable
    else:
        class_type = _RULE_TYPEMAP[type_tag]

    return class_type(**dict_data)
