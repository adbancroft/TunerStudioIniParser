from dataclasses import InitVar, dataclass, field
from abc import abstractmethod
from typing import Dict, Any, List, TypeVar, Generic, Optional


DictItem = TypeVar('DictItem')


@dataclass(eq=False)
class _DictBase(Generic[DictItem], Dict[Any, DictItem]):
    dict_data: InitVar[Dict[Any, DictItem]]

    def __post_init__(self, dict_data: Dict[Any, DictItem]):
        dict.__init__(self, dict_data)


@dataclass(eq=False)
class _SectionBase:
    name: str

    @property
    def key(self):
        return self.name


@dataclass(eq=False)
class DictSection(_SectionBase, _DictBase[DictItem]):
    # pylint: disable=too-many-ancestors
    pass


@dataclass(eq=False)
class Section(_SectionBase):
    lines: list


@dataclass(eq=False)
class KeyValuePair():
    name: str
    values: list


@dataclass(eq=False)
class Variable:
    name: str

    @property
    def key(self):
        return self.name


@dataclass
class DataType:
    type_name: str
    c_typename: str
    width: int


_data_types = {
    'U08': DataType(type_name='U08', c_typename='uint8_t', width=1),
    'S08': DataType(type_name='S08', c_typename='int8_t', width=1),
    'U16': DataType(type_name='U16', c_typename='uint16_t', width=2),
    'S16': DataType(type_name='S16', c_typename='int16_t', width=2),
    'U32': DataType(type_name='U32', c_typename='uint32_t', width=4),
    'S32': DataType(type_name='S32', c_typename='int32_t', width=4),
    'F32': DataType(type_name='U08', c_typename='float', width=4),
}


@dataclass(eq=False)
class _TypedVariable(Variable):
    type_name: InitVar[str]
    data_type: DataType = field(init=False)

    def __post_init__(self, type_name: str):
        self.data_type = _data_types[type_name]

    @property
    @abstractmethod
    def size(self) -> int:
        """Size of the variable in bytes"""


@dataclass(eq=False)
class BitSize:
    start_bit: int
    bit_length: int


@dataclass(eq=False)
class BitVariable(_TypedVariable):
    bit_size: BitSize
    offset: Optional[int] = None
    unknown_values: Optional[List[Any]] = None

    @property
    def size(self) -> int:
        return self.data_type.width


@dataclass(eq=False)
class _ScalarCore:
    # pylint: disable=too-many-instance-attributes
    units: Optional[str] = None
    scale: Optional[float] = None
    translate: Optional[float] = None
    low: Optional[float] = None
    high: Optional[float] = None
    digits: Optional[int] = None
    offset: Optional[int] = None
    unknown_values: Optional[List[Any]] = None


@dataclass(eq=False)
class ScalarVariable(_ScalarCore, _TypedVariable):

    @property
    def size(self) -> int:
        return self.data_type.width


@dataclass(eq=False)
class _Array1dCore(_TypedVariable):
    dim1d: int

    @property
    def size(self) -> int:
        return self.dim1d * self.data_type.width

@dataclass(eq=False)
class Array1dVariable(_ScalarCore, _Array1dCore):
    pass


@dataclass(eq=False)
class MatrixDimensions:
    xsize: int
    ysize: int


@dataclass(eq=False)
class _Array2dCore(_TypedVariable):
    dim2d: MatrixDimensions

    @property
    def size(self) -> int:
        return self.dim2d.xsize * self.dim2d.ysize * self.data_type.width


@dataclass(eq=False)
class Array2dVariable(_ScalarCore, _Array2dCore):
    pass


@dataclass(eq=False)
class StringVariable(Variable):
    length: int
    encoding: str
    unknown_values: Optional[List[Any]] = None

    @property
    def size(self) -> int:
        return self.length


@dataclass(eq=False)
class Page(_DictBase[Variable]):
    page_num: int

    @property
    def key(self):
        return self.page_num


@dataclass(eq=False)
class ConstantsSection(DictSection[Page]):
    header_lines: list


@dataclass(eq=False)
class AxisBin:
    constant_ref: str
    outputchannel: Optional[str] = None
    unknown: Optional[str] = None


@dataclass(eq=False)
class Table:
    # pylint: disable=too-many-instance-attributes
    table_id: str
    map3d_id: str
    title: str
    page_num: int
    xbins: AxisBin
    ybins: AxisBin
    zbins: AxisBin
    unknown_values: Optional[List[Any]] = None
    xy_labels: Optional[List[str]] = None
    grid_height: Optional[float] = None
    grid_orient: Optional[List[float]] = None
    updown_labels: Optional[List[str]] = None
    help_topic: Optional[str] = None

    @property
    def key(self):
        return self.table_id


@dataclass(eq=False)
class Axis:
    min: int
    max: int
    step: int


@dataclass(eq=False)
class Curve:
    # pylint: disable=too-many-instance-attributes
    curve_id: str
    name: str
    column_labels: List[str]
    xaxis_limits: Axis
    xbins: AxisBin
    yaxis_limits: Axis
    ybins: AxisBin
    curve_dimensions: Optional[MatrixDimensions] = None
    curve_gauge: Optional[str] = None
    line_label: Optional[List[str]] = None

    @property
    def key(self):
        return self.curve_id


@dataclass(eq=False)
class TsIniFile(_DictBase[_SectionBase]):
    file_header: List

    def __post_init__(self, dict_data: Dict[Any, _SectionBase]):
        super().__post_init__(dict_data)
        self._wire_constants()

    def _wire_constants(self):
        for table in self['TableEditor'].values():
            self._wire_table(table)
        for table in self['CurveEditor'].values():
            self._wire_curve(table)

    def _wire_table(self, table):
        def set_bin_constant(bin_field, page):
            bin_field.constant_ref = page[bin_field.constant_ref]

        page = self['Constants'][table.page_num]

        set_bin_constant(table.xbins, page)
        set_bin_constant(table.ybins, page)
        set_bin_constant(table.zbins, page)

    def _find_constant_nothrow(self, name, expected_type):
        for page in self['Constants'].values():
            constant = page.get(name)
            if constant and isinstance(constant, expected_type):
                return constant
        return None

    def _find_constant(self, name, expected_type):
        constant = self._find_constant_nothrow(name, expected_type)
        if not constant:
            raise KeyError(name)
        return constant

    def _find_pcvariable_nothrow(self, name, expected_type):
        variable = self['PcVariables'].get(name)
        return variable if isinstance(variable, expected_type) else None

    def _find_named_variable_nothrow(self, name, expected_type):
        constant = self._find_constant_nothrow(name, expected_type)
        return constant if constant else self._find_pcvariable_nothrow(name, expected_type)

    def _find_named_variable(self, name, expected_type):
        constant = self._find_named_variable_nothrow(name, expected_type)
        if not constant:
            raise KeyError(name)
        return constant

    def _wire_curve(self, curve):
        def set_bin_constant(bin_field):
            bin_field.constant_ref = self._find_named_variable(bin_field.constant_ref, Array1dVariable)  # noqa: E501

        set_bin_constant(curve.xbins)
        if isinstance(curve.ybins, list):
            for ybin in curve.ybins:
                set_bin_constant(ybin)
        else:
            set_bin_constant(curve.ybins)
