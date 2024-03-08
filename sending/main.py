import sys
sys.path.append("..")

import strategies
import utils
import time


def main():
    project = utils.dict_query("select * from projects where name='pa'")[0]
    database = utils.get_database_name_from_project_id(project["id"])
    strategies.send_not_sent_messages(database)

# project = utils.dict_query("select * from projects where name='pa'")[0]
# strategies.create_new_campaign_with_available_addresses('pa')
main()
