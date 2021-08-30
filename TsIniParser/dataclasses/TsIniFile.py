from dataclasses import InitVar, dataclass
from abc import ABC, abstractmethod
from typing import Dict, Any, List, TypeVar, Generic
from .dataclass_utils import from_existing


class is_keyed(ABC):
    @abstractmethod
    def key(self):
        pass


DictItem = TypeVar('DictItem')


@dataclass
class DictBase(Generic[DictItem], Dict[Any, DictItem]):
    dict_data: InitVar[Dict[Any, DictItem]]

    def __post_init__(self, dict_data: Dict[Any, DictItem]):
        dict.__init__(self, dict_data)


@dataclass
class AbstractSection(is_keyed):
    name: str

    @property
    def key(self):
        return self.name

    @abstractmethod
    def is_empty(self):
        pass


@dataclass
class DictSection(AbstractSection, DictBase[DictItem]):

    def is_empty(self):
        return len(self) == 0


@dataclass
class Section(AbstractSection):
    lines: list

    def is_empty(self):
        return len(self.lines) == 0


@dataclass
class KeyValuePair(is_keyed):
    key_name: str
    values: list

    @property
    def key(self):
        return self.kvp_key


@dataclass
class Variable(is_keyed):
    name: str
    unknown_values: list = None

    @property
    def key(self):
        return self.name


@dataclass
class TypedVariable(Variable):
    data_type: str = ''


@dataclass
class BitVariable(TypedVariable):
    bit_size: list = None
    offset: int = None


@dataclass
class ScalarVariable(TypedVariable):
    units: str = None
    scale: float = None
    translate: float = None
    low: float = None
    high: float = None
    digits: int = None
    offset: int = None


@dataclass
class Array1dVariable(ScalarVariable):
    dim1d: int = 0


@dataclass
class Array2dVariable(ScalarVariable):
    dim2d: list = None


@dataclass
class StringVariable(Variable):
    encoding: str = ''
    length: int = 0


@dataclass
class Page(is_keyed, DictBase[Variable]):
    page_num: int

    @property
    def key(self):
        return self.page_num


@dataclass
class ConstantsSection(DictSection[Page]):
    header_lines: list


@dataclass
class AxisBin:
    constant_ref: str
    outputchannel: str = None
    unknown: str = None


@dataclass
class Table(is_keyed):
    table_id: str
    map3d_id: str
    title: str
    page_num: int
    xbins: AxisBin
    ybins: AxisBin
    zbins: AxisBin
    unknown_values: list = None
    xy_labels: list = None
    grid_height: float = None
    grid_orient: list = None
    updown_labels: list = None
    help_topic: str = None

    @property
    def key(self):
        return self.table_id


@dataclass
class TableArray1dVariable(Array1dVariable):
    table: Table = None


@dataclass
class TableArray2dVariable(Array2dVariable):
    table: Table = None


@dataclass
class Axis:
    min: int
    max: int
    step: int


@dataclass
class Curve(is_keyed):
    curve_id: str
    name: str
    columnlabels: list
    xaxis_limits: Axis
    xbins: AxisBin
    yaxis_limits: Axis
    ybins: AxisBin
    size: list = None
    gauge: str = ''
    line_label: list = None

    @property
    def key(self):
        return self.curve_id


@dataclass
class CurveArray1dVariable(Array1dVariable):
    curve: Curve = None


@dataclass
class TsIniFile(DictBase[AbstractSection]):
    file_header: List

    def __post_init__(self, dict: Dict[Any, AbstractSection]):
        super().__post_init__(dict)
        self._wire_constants()

    def _wire_constants(self):
        for table in self['TableEditor'].values():
            self._wire_table(table)
        for table in self['CurveEditor'].values():
            self._wire_curve(table)

    def _wire_table(self, table):
        def set_bin_constant(bin, page, type):
            original_variable = page[bin.constant_ref]
            if not isinstance(original_variable, type):
                new_instance = from_existing(original_variable, type, {'table': table})
                page[bin.constant_ref] = new_instance
            else:
                new_instance = original_variable
            bin.constant_ref = new_instance

        page = self['Constants'][table.page_num]

        set_bin_constant(table.xbins, page, TableArray1dVariable)
        set_bin_constant(table.ybins, page, TableArray1dVariable)
        set_bin_constant(table.zbins, page, TableArray2dVariable)

    def _find_constant_nothrow(self, name, type):
        for page in self['Constants'].values():
            constant = page.get(name)
            if constant and isinstance(constant, type):
                return constant
        return None

    def _find_constant(self, name, type):
        constant = self._find_constant_nothrow(name, type)
        if not constant:
            raise KeyError(name)
        return constant

    def _find_pcvariable_nothrow(self, name, type):
        variable = self['PcVariables'].get(name)
        return variable if isinstance(variable, type) else None

    def _find_named_variable_nothrow(self, name, type):
        constant = self._find_constant_nothrow(name, type)
        return constant if constant else self._find_pcvariable_nothrow(name, type)

    def _find_named_variable(self, name, type):
        constant = self._find_named_variable_nothrow(name, type)
        if not constant:
            raise KeyError(name)
        return constant

    def _replace_constant(self, name, original_instance, new_instance):
        for page in self['Constants'].values():
            if page.get(name) == original_instance:
                page[name] = new_instance
                return True
        return False

    def _replace_variable(self, name, original_instance, new_instance):
        if self['PcVariables'].get(name) == original_instance:
            self['PcVariables'][name] = new_instance
            return True
        return False

    def _replace_named_variable(self, name, original_instance, new_instance):
        if not self._replace_constant(name, original_instance, new_instance):
            return self._replace_variable(name, original_instance, new_instance)

    def _wire_curve(self, curve):
        def set_bin_constant(bin):
            original_variable = self._find_named_variable(bin.constant_ref, Array1dVariable)  # noqa: E501
            if not isinstance(original_variable, CurveArray1dVariable):
                new_instance = from_existing(original_variable, CurveArray1dVariable, {'curve': curve})  # noqa: E501
                self._replace_named_variable(bin.constant_ref, original_variable, new_instance)  # noqa: E501
            else:
                new_instance = original_variable
            bin.constant_ref = new_instance

        set_bin_constant(curve.xbins)
        if isinstance(curve.ybins, list):
            for bin in curve.ybins:
                set_bin_constant(bin)
        else:
            set_bin_constant(curve.ybins)
