import sys

sys.path.append("..")

import strategies
import utils
import time
import datetime


def main():
    project = utils.dict_query("select * from projects where name='HR'")[0]
    database = utils.get_database_name_from_project_id(project["id"])

    while True:
        print(f"Evaluating creation of campaign of day {datetime.datetime.now()}")
        strategies.create_new_campaign_with_available_addresses(database)


main()
