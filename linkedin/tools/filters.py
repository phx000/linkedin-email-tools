from . import db
import utils
import config


def merge_filters(old_list, new_list):
    old_list = old_list.copy()
    for new_filter in new_list:
        if new_filter["type"] in [old_filter["type"] for old_filter in old_list]:
            old_filter = next(el for el in old_list if el["type"] == new_filter["type"])
            for value in new_filter["values"]:
                if value not in old_filter["values"]:
                    old_filter["values"].append(value)
        else:
            old_list.append(new_filter)
    return old_list


def generate_all_possible_filters(filter_):
    out = []
    for value in filter_["values"]:
        new_filter = filter_.copy()
        new_filter["values"] = [value]
        out.append([new_filter])
    return out


def ruleset_to_requests(ruleset, requests_type, project_id=None):
    first_filter = ruleset["filters"][0]
    all_other_filters = ruleset["filters"][1:]
    new_filters = generate_all_possible_filters(first_filter)

    if "initial" in ruleset and "filters" in ruleset["initial"]:
        new_filters = [merge_filters(ruleset["initial"]["filters"], new_filter) for new_filter in new_filters]

    new_rules = [{"spell_check": ruleset["spell_check"], "filters": new_filter} for new_filter in new_filters]

    if "initial" in ruleset and "keywords" in ruleset["initial"]:
        for new_rule in new_rules:
            new_rule["keywords"] = (ruleset["initial"]["keywords"])

    for new_rule in new_rules:
        db.create_request_record(requests_type, new_rule, all_other_filters, 0, project_id)


def update_initial_filters(ruleset, new_filters):
    ruleset = ruleset.copy()
    old_initial_filters = []
    if "initial" not in ruleset:
        ruleset["initial"] = {}

    if "filters" in ruleset["initial"]:
        old_initial_filters = ruleset["initial"]["filters"].copy()
        old_initial_filters = [f for f in old_initial_filters if f["type"] != "CurrentCompany"]

    merged_filters = merge_filters(old_initial_filters, new_filters)
    ruleset["initial"]["filters"] = merged_filters
    return ruleset


def build_all_leads_requests(project):
    database = utils.get_database_name_from_project_id(project["id"])
    not_fetched_companies = utils.dict_query("select id,urn from accounts where requested=false order by employee_count_range desc nulls last, id limit %s", (config.LINKEDIN__BUILD_LEAD_REQUESTS_AMOUNT,),
                                             database=database)
    conn = utils.connection(database)
    cursor = conn.cursor()

    for company in not_fetched_companies:
        current_company_filter = {"type": "CurrentCompany", "values_type": "values_list", "values": [{"type": "id", "value": company["urn"], "accounts_pk": company["id"]}]}
        for ruleset in project["linkedin__leads"]:
            updated_ruleset = update_initial_filters(ruleset, [current_company_filter])
            ruleset_to_requests(updated_ruleset, True, project_id=project["id"])
        cursor.execute("update accounts set requested=true where id=%s", (company["id"],))

    conn.commit()
    conn.close()
