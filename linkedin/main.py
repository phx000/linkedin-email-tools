import sys
sys.path.append("..")

import utils
from tools import db, filters
import strategies
import json
import time
import datetime
import config


def start_project(project):
    for ruleset in project["linkedin__accounts"]:
        filters.ruleset_to_requests(ruleset, False, project_id=project["id"])


def restart_project(project):
    database = utils.get_database_name_from_project_id(project["id"])
    utils.query("delete from requests where id>0", commit=True)
    utils.query("delete from accounts where id>0", commit=True, database=database)
    utils.query("delete from leads where id>0", commit=True, database=database)
    # start_project(project)


def push_acc_config(project):
    with open(r"C:\Users\Philip\Documents\Prometheus\junk\test_rules.json", "r", encoding="utf8") as file:
        data = json.load(file)
    utils.query("update projects set linkedin__accounts=%s where id=%s", (json.dumps(data), project["id"],), commit=True)


def main():
    while True:
        if datetime.datetime.now().hour >= config.LINKEDIN__STARTING_HOUR:
            print("Valid time. Working")
            project = db.get_unfinished_project()
            if project is None:
                print("All projects are finished")
                return

            while True:
                result = strategies.simple_search(project)
                if result is None:
                    print("Finished this project")
                    db.flag_project_as_finished(project)

                print("Highest level return code:", result)

                if result == -2:
                    print("Stopping because all accounts 429")
                    print("Sleeping until next day")
                    current_datetime = datetime.datetime.now()
                    seconds_until_next_day = (24 - current_datetime.hour - 1) * 3600 + (60 - current_datetime.minute + 5) * 60
                    time.sleep(seconds_until_next_day)

                print("")
        else:
            print("Sleeping")
            time.sleep(600)


main()

# project = utils.dict_query("select * from projects where name='HR'")[0]
# start_project(project)
