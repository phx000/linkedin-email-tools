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
        project = utils.dict_query("select * from projects where name='HR'")[0]
        strategies.generate_addresses_from_all_leads(project)
        validation_upload_all_possible(project)
        print("Sleeping")
        time.sleep(config.ADDRESSING__SECONDS_OF_SLEEP_BETWEEN_GENERATIONS)


main()
