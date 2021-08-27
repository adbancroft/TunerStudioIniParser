from .TsIniFile import *

# Type tag to type mapping
_RULE_TYPEMAP = {
        'kvp_bits_line' : BitVariable,
        'kvp_scalar_line' : ScalarVariable, 
        'kvp_array_line' : Array1dVariable, 
        'kvp_string_line' : StringVariable,
        'kvp_line' : KeyValuePair,
        'page' : Page,
        'constants_section': ConstantsSection,
        'pcvariables_section': DictSection[Variable],
        'context_help_section': DictSection[str],
        'axis_bin': AxisBin,
        'table': Table,
        'tableeditor_section': DictSection[Table],
        'axis_limits': Axis,
        'curve': Curve,
        'curveeditor_section': DictSection[Curve],
        'generic_section': Section,
        'start': TsIniFile,
    }

def dataclass_factory(type_tag:str, dict_data:Dict[str,Any]):

    """ A factory that converts a type marker and dictionary into a class instance"""
    
    if 'kvp_array_line'==type_tag:
        if 'dim1d' in dict_data:
            type = Array1dVariable
        else:
            type = Array2dVariable
    else:
        type = _RULE_TYPEMAP[type_tag]
    
    return type(**dict_data)