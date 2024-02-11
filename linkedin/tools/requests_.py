from linkedin.sales_api import sales, sales_filters
from linkedin.tools import filters
from linkedin.tools import db


def build_range_value(min_, max_):
    range_value_cls = getattr(sales_filters, "RangeValue")
    return range_value_cls(min_, max_)


def build_values_list(values):
    value_instances = []
    list_value_cls = getattr(sales_filters, "ListValue")
    for value in values:
        if value["type"] == "id":
            value_instances.append(list_value_cls(id_=value["value"]))
        else:
            value_instances.append(list_value_cls(text=value["value"]))

    values_cls = getattr(sales_filters, "Values")
    return values_cls(value_instances)


def build_filter(filter_):
    if filter_["values_type"] == "range_value":
        values = filter_["values"]
        values_instance = build_range_value(values[0], values[1])
    else:
        values_instance = build_values_list(filter_["values"])

    filter_cls = getattr(sales_filters, filter_["type"])
    return filter_cls(values_instance)


def build_search_instance(request):
    data = request["data"]
    filters = None

    if "filters" in data:
        filters = []
        for filter_ in data["filters"]:
            filters.append(build_filter(filter_))

    keywords = data["keywords"] if "keywords" in data else None
    return sales.AccountSearch(filters, keywords=keywords, start=request["start"], spell_correction_enabled=data["spell_check"])


def create_child_requests(request):
    old_filters = request["data"]["filters"]
    new_filter = request["data_children"][0]
    data_children = request["data_children"][1:]

    for value in new_filter["values"]:
        single_value_filter = new_filter.copy()
        single_value_filter["values"] = [value]
        combined_filters = filters.merge_filters(old_filters, [single_value_filter])

        data = request["data"].copy()
        data["filters"] = combined_filters
        db.create_request_record(request["type"], data, data_children, 0, request["project"])


def create_next_request_chunk(request):
    db.create_request_record(request["type"], request["data"], request["data_children"], request["start"] + 100, request["project"])


def save_search(result, request_type):
    print("paging_total", result["paging"]["total"])
