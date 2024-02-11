from tools import db
import search


def main():
    project = db.get_unfinished_project()
    # start_project.start_project(project)
    # return
    if project is None:
        print("All projects are finished")
        return

    while True:
        request = db.get_unfinished_request(project)
        if request is None:
            print("Finished this project")
            db.flag_project_as_finished(project)
            return

        code = search.execute_request(request)

        print("Highest level return code:", code)

        # if code == -1:
        #     print("Stopping execution of requests")
        #     return

        # print("Good return")
        return


main()

# req = utils.dict_query("select * from requests where id=285")[0]
#
# from tools import requests_
#
# requests_.create_next_request_chunk(req)
