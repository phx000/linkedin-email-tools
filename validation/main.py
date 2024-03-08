import sys

sys.path.append("..")

import strategies
import utils
import time


def main():
    project = utils.dict_query("select * from projects where name='pa'")[0]
    while True:
        strategies.find_all_non_fetched_validation_files(project)
        print("Sleeping")
        time.sleep(100)


project = utils.dict_query("select * from projects where name='pa'")[0]
# strategies.validation_upload_all_possible(project)

strategies.find_all_non_fetched_validation_files(project)
# main()
