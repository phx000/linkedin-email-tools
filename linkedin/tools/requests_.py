import utils
from linkedin.sales_api import sales, sales_filters
from linkedin.tools import filters, db, cleaning


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
    return sales.Search(request["type"], filters, keywords=keywords, start=request["start"], spell_correction_enabled=data["spell_check"])


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


def save_search(result, request):
    database_name = utils.get_database_name_from_project_id(request["project"])
    if request["type"] == False:  # meaning if the request is an Account search
        clean_result = cleaning.clean_account_search_result(result)
        utils.dicts_commit("insert into accounts (name, urn, employee_count_range, industry) values (%s,%s,%s,%s) on conflict do nothing",
                           ("name", "urn", "employee_count_range", "industry"), clean_result, database=database_name)

        print(f"Saving comps: {len(clean_result)}/{len(result['elements'])}")

    else:
        clean_result = cleaning.clean_lead_search_result(result)
        for filter_ in request["data"]["filters"]:
            if filter_["type"] == "CurrentCompany":
                for clean in clean_result:
                    clean["search_company_urn"] = filter_["values"][0]["value"]
                break

        print(f"Saving people: {len(clean_result)}/{len(result['elements'])}")

        utils.dicts_commit(
            "insert into leads (first_name, last_name, urn, company_urn, search_company_urn, title, geo_region, started_position_on_month, started_position_on_year) values (%s,%s,%s,%s,%s,%s,%s,%s,%s) on conflict do nothing",
            ("first_name", "last_name", "urn", "company_urn", "search_company_urn", "title", "geo_region", "started_position_on_month", "started_position_on_year"), clean_result,
            database=database_name)
