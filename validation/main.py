import sys
sys.path.append("..")

import strategies
import utils
import time


def main():
    project = utils.dict_query("select * from projects where name='HR'")[0]
    while True:
        strategies.find_all_non_fetched_validation_files(project)
        print("Sleeping")
        time.sleep(100)


main()
