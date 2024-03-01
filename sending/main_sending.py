import sys
sys.path.append("..")

import strategies
import utils
import time


def main():
    project = utils.dict_query("select * from projects where name='HR'")[0]
    database = utils.get_database_name_from_project_id(project["id"])
    while True:
        strategies.send_not_sent_messages(database)
        print("Sleeping")
        time.sleep(10)


main()
