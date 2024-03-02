import sys

sys.path.append("..")

import strategies
import utils
import time


def main():
    while True:
        project = utils.dict_query("select * from projects where name='HR'")[0]
        strategies.simple_strategy(project)
        break


main()
