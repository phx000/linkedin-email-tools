import json
from tools import db, requests_
import utils, config
from sales_api.session import Session

session = Session()


def search_request(request):
    request = requests_.build_search_instance(request)
    while True:
        account = session.get_account()
        if account is None:
            return None
        code, content = request.search(account["data"])
        if code == 429:
            session.flag_account(account["id"], 429)
            continue
        if code != 200:
            comment = {"http_error": code, "error_content": str(content)[:1000]}
            utils.add_comment(comment, "sales_accounts", request["id"])
            session.flag_account(account["id"], 429)
            continue
        return content


def handle_search_result(result, request):
    result = json.loads(result)
    total_results = result["paging"]["total"]
    if total_results == 0:
        return
    if total_results > config.LINKEDIN__MAX_RESULTS_PER_SEARCH and request["data_children"]:
        requests_.create_child_requests(request)
    else:
        if len(result["elements"]) == 100:
            requests_.create_next_request_chunk(request)
    requests_.save_search(result, request["type"])


def execute_request(request):
    try:
        search_result = search_request(request)
    except Exception as e:
        comment = utils.stringify_exception(e)
        utils.add_comment(comment, "requests", request["id"])
        db.register_request_result(request["id"], 2)
        return 2

    if search_result is None:
        return -2

    try:
        handle_search_result(search_result, request)
    except Exception as e:
        comment = utils.stringify_exception(e)
        utils.add_comment(comment, "requests", request["id"])
        db.register_request_result(request["id"], 2)
        return 2

    db.register_request_result(request["id"], 1)
    return 1
