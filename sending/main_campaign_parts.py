import sys

sys.path.append("..")

import strategies
import utils
import time


def main():
    project = utils.dict_query("select * from projects where name='HR'")[0]
    database = utils.get_database_name_from_project_id(project["id"])

    while True:
        campaigns_ = utils.dict_query("select * from campaigns where status=false", database=database)
        if campaigns_:
            strategies.create_new_messages_from_campaign_parts(campaigns_, database)
        else:
            print(" - All campaigns finished")
        time.sleep(10)



main()
