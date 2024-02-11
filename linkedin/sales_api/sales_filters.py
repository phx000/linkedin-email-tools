class RangeValue:
    def __init__(self, min_, max_):
        self.min_ = min_
        self.max_ = max_

    def __repr__(self):
        return f"rangeValue:(min:{self.min_},max:{self.max_})"


class ListValue:
    def __init__(self, id_=None, text=None, selection_type=True):
        if id_ is None and text is None:
            raise Exception("'id' and 'text' fields cannot be both None")

        if id_ is not None:
            self.field_type = "id"
            self.field_value = id_
        else:
            self.field_type = "text"
            self.field_value = text

        self.selection_type = selection_type

    def __repr__(self):
        return f"({self.field_type}:{self.field_value},selectionType:{'INCLUDED' if self.selection_type else 'EXCLUDED'})"


class Values:
    def __init__(self, values):
        self.values = values

    def __repr__(self):
        return f"values:List({','.join([str(el) for el in self.values])})"


class AnnualRevenue:
    def __init__(self, range_value, selected_subfilter="USD"):
        self.range_value = range_value
        self.selected_subfilter = selected_subfilter

    def __repr__(self):
        return f"(type:ANNUAL_REVENUE,{self.range_value},selectedSubFilter:{self.selected_subfilter})"


class CompanyHeadcount:
    def __init__(self, values):
        self.values = values

    def __repr__(self):
        return f"(type:COMPANY_HEADCOUNT,{self.values})"


class CompanyHeadcountGrowth:
    def __init__(self, range_value):
        self.range_value = range_value

    def __repr__(self):
        return f"(type:COMPANY_HEADCOUNT_GROWTH,{self.range_value})"


class Region:
    def __init__(self, values):
        self.values = values

    def __repr__(self):
        return f"(type:REGION,{self.values})"


class Industry:
    def __init__(self, values):
        self.values = values

    def __repr__(self):
        return f"(type:INDUSTRY,{self.values})"
