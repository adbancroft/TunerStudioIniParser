from dataclasses import InitVar, dataclass, field
from abc import abstractmethod
from typing import Dict, Any, Iterable, List, Mapping, Optional
from collections import UserDict, UserList


@dataclass(eq=False)
class _DictBase(UserDict):
    dict_data: InitVar[Mapping]

    def __post_init__(self, dict_data: Mapping):
        super().__init__(dict_data)


@dataclass(eq=False)
class _SectionBase:
    name: str

    @property
    def key(self):
        return self.name


@dataclass(eq=False)
class DictSection(_SectionBase, _DictBase):
    # pylint: disable=too-many-ancestors
    pass


@dataclass(eq=False)
class Section(_SectionBase, UserList):
    lines: InitVar[Iterable]

    def __post_init__(self, lines: Iterable):
        UserList.__init__(self, lines)


@dataclass(eq=False)
class KeyValuePair():
    name: str
    values: list

    @property
    def key(self):
        return self.name


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
    offset: Optional[int] = None
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
    variable: str
    outputchannel: Optional[str] = None


@dataclass(eq=False)
class Table:
    # pylint: disable=too-many-instance-attributes
    table_id: str
    map3d_id: str
    title: str
    page_num: int
    table_xbin: AxisBin
    table_ybin: AxisBin
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


@dataclass
class Axis:
    min: int
    max: int
    step: int


@dataclass(eq=False)
class CurveLine:
    xbin: AxisBin
    ybin: AxisBin
    column_label: str
    line_label: str
    xaxis: Axis
    yaxis: Axis


@dataclass(eq=False)
class Curve:
    # pylint: disable=too-many-instance-attributes
    curve_id: str
    name: str
    lines: List[CurveLine] = field(default_factory=list, init=False)

    xaxis_limits: InitVar[List[Axis]]
    yaxis_limits: InitVar[List[Axis]]
    xbins: InitVar[List[AxisBin]]
    ybins: InitVar[List[AxisBin]]
    column_labels: InitVar[Optional[List[str]]] = None
    line_label: InitVar[Optional[List[str]]] = None

    page_num: Optional[int] = None
    curve_dimensions: Optional[MatrixDimensions] = None
    curve_gauge: Optional[str] = None
    help_topic: Optional[str] = None

    @property
    def key(self):
        return self.curve_id

    def __post_init__(self,
                      xaxis_limits: List[Axis],
                      yaxis_limits: List[Axis],
                      xbins: List[AxisBin],
                      ybins: List[AxisBin],
                      column_labels: List[str],
                      line_label: List[str]
                      ):
        # Normalize the incoming arrays to the length of ybins
        count = len(ybins)
        column_labels = column_labels[:count] if column_labels else []
        column_labels = column_labels + [''] * (count - len(column_labels))
        line_label = line_label[:count] if line_label else []
        line_label = line_label + [''] * (count - len(line_label))
        xbins = xbins + [xbins[-1]] * (count - len(xbins))
        xaxis_limits = xaxis_limits + [xaxis_limits[-1]] * (count - len(xaxis_limits))
        yaxis_limits = yaxis_limits + [yaxis_limits[-1]] * (count - len(yaxis_limits))

        for composite in zip(xbins, ybins, column_labels, line_label, xaxis_limits, yaxis_limits):
            self.lines.append(CurveLine(xbin=composite[0],
                                        ybin=composite[1],
                                        column_label=composite[2],
                                        line_label=composite[3],
                                        xaxis=composite[4],
                                        yaxis=composite[5]))


@dataclass(eq=False)
class TsIniFile(_DictBase[_SectionBase]):
    file_header: List

    def __post_init__(self, dict_data: Dict[Any, _SectionBase]):
        super().__post_init__(dict_data)
        self._wire_constants()

    def _wire_constants(self):
        if 'TableEditor' in self:
            for table in self['TableEditor'].values():
                self._wire_table(table)
        if 'CurveEditor' in self:
            for curve in self['CurveEditor'].values():
                self._wire_curve(curve)

    def _find_constant_nothrow(self, name, expected_type):
        for page in self['Constants'].values():
            constant = page.get(name)
            if constant and isinstance(constant, expected_type):
                return constant
        return None

    def _find_pcvariable_nothrow(self, name, expected_type):
        if 'PcVariables' in self:
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

    def _set_bin_variable(self, bin_field: AxisBin, var_type: type):
        if isinstance(bin_field.variable, str):
            bin_field.variable = self._find_named_variable(bin_field.variable, var_type)  # noqa: E501
        # TODO
        # Wire in output channel (once the OutputChannels section is properly parsed)

    def _wire_curve(self, curve: Curve):
        def wire_curve_bin(bin: CurveLine):
            self._set_bin_variable(bin.xbin, Array1dVariable)
            self._set_bin_variable(bin.ybin, Array1dVariable)

        for bin in curve.lines:
            wire_curve_bin(bin)

    def _wire_table(self, table):
        self._set_bin_variable(table.table_xbin, Array1dVariable)
        self._set_bin_variable(table.table_ybin, Array1dVariable)
        self._set_bin_variable(table.zbins, Array2dVariable)
