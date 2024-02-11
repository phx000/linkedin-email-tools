from tools import filters, db


def start_ruleset(ruleset, project_id=None):
    first_filter = ruleset["filters"][0]
    all_other_filters = ruleset["filters"][1:]
    new_filters = filters.generate_all_possible_filters(first_filter)

    if "initial" in ruleset:
        new_filters = [filters.merge_filters(ruleset["initial"]["filters"], new_filter) for new_filter in new_filters]

    new_rules = [{"spell_check": ruleset["spell_check"], "filters": new_filter} for new_filter in new_filters]

    if "initial" in ruleset and "keywords" in ruleset["initial"]:
        for new_rule in new_rules:
            new_rule["keywords"] = (ruleset["initial"]["keywords"])

    for new_rule in new_rules:
        db.create_request_record(False, new_rule, all_other_filters, 0, project_id)


def start_project(project):
    for ruleset in project["linkedin_accounts"]:
        start_ruleset(ruleset, project_id=project["id"])
