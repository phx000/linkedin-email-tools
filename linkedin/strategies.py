import utils, search
from sales_api import sales_filters
from tools import filters
import config


def simple_search(project):
    filters.build_all_leads_requests(project)
    request = utils.dict_query("""select * from requests where type = true and status = 0 and project =%s order by creation_timestamp desc, start desc, id limit 1""", (project["id"],))

    # request = utils.dict_query("select * from requests where type=false and status=0 and project=%s order by id limit 1", (project["id"],))

    if not request:
        request = utils.dict_query("select * from requests where type=false and status=0 and project=%s order by id limit 1", (project["id"],))
        if not request:
            return
    print(f"-- type:{request[0]['type']}, id:{request[0]['id']} --")
    return search.execute_request(request[0])
