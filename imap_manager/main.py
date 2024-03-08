import sys

sys.path.append("..")

import strategies
from tools import imap
import utils
import time


def main():
    while True:
        project = utils.dict_query("select * from projects where name='pa'")[0]
        database = utils.get_database_name_from_project_id(project["id"])
        mailservers = utils.dict_query("select * from mailservers", database=database)
        imap.create_imap_connections(mailservers)
        strategies.simple_strategy(mailservers, project)
        time.sleep(15)


main()
