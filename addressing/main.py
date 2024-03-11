import sys

sys.path.append("..")

import strategies
import utils
import time
import config
from validation.strategies import validation_upload_all_possible


def main():
    while True:
        print("Generating")
        project = utils.dict_query("select * from projects where name='pa'")[0]
        strategies.generate_addresses_from_all_non_used_leads(project)
        validation_upload_all_possible(project)
        print("Sleeping")
        time.sleep(config.ADDRESSING__SECONDS_OF_SLEEP_BETWEEN_GENERATIONS)


# main()
project = utils.dict_query("select * from projects where id=2")[0]
database = utils.get_database_name_from_project_id(project["id"])
strategies.generate_addresses_from_all_non_used_leads(project)
