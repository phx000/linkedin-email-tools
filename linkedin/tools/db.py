import utils
import json


def get_unfinished_project():
    # data = utils.dict_query("select * from projects where status=0 order by priority desc limit 1")
    # return data[0] if data else None
    data = utils.dict_query("select * from projects where name=%s", ("HR",))
    return data[0] if data else None


def get_unfinished_request(project):
    data = utils.dict_query("select * from requests where project=%s and status=0 order by id", (project["id"],))
    return data[0] if data else None


def flag_project_as_finished(project):
    utils.query("update projects set status=1 where id=%s", (project["id"],), commit=True)


def register_request_result(request_id, result):
    utils.query("update requests set status=%s where id=%s", (result, request_id,), commit=True)


def create_request_record(type_, data, data_children, start, project):
    utils.query("insert into requests (type, data, data_children, start, project, status) values (%s, %s, %s, %s, %s, 0)",
                (type_, json.dumps(data), json.dumps(data_children), start, project), commit=True)
