import utils
import config
import rocketreach
import time


def simple_search(project):
    database = utils.get_database_name_from_project_id(project["id"])
    records = utils.dict_query("select * from rocketreach where rr_id != '-1' and format is null", database=database)
    if not records:
        print("Found no records")
        accounts = utils.dict_query(config.FORMATS__SIMPLE_SEARCH_STRATEGY_GET_ACCOUNTS_QUERY, database=database)
        if not accounts:
            print("No more accounts to search formats for")
            return

        for account in accounts:
            break_for_loop_flag = False
            while True:
                print("Looking for rr_id")
                result = rocketreach.get_rocketreach_id_from_account_name(account["name"])
                if result == -2:
                    print("Got 500 looking for rr_id")
                    records = utils.dict_query("select * from rocketreach where rr_id != '-1' and format is null limit 1", database=database)
                    if records:
                        print("Found records with rr_ids without format. Breaking and passing to format-finder")
                        break_for_loop_flag = True
                    print("No records with rr_ids without format. Sleeping for 300s")
                    time.sleep(300)
                break
            if break_for_loop_flag:
                print("Breaking out of the for loop. Going to find format from name section")
                break
            print("Saving new record")
            utils.query("insert into rocketreach (account_fk, rr_id) values (%s,%s)", (account["id"], result), commit=True, database=database)

    for record in records:
        print("Finding format for rr_id")
        result = rocketreach.get_rocketreach_format_from_rocketreach_id(record["rr_id"])
        if result == -2:
            print("Finding of format for rr_id returned 429. Sleeping for 60s")
            time.sleep(60)
            continue
        print("Updating record and sleeping for 60s")
        utils.query("update rocketreach set format=%s where id=%s", (result, record["id"]), commit=True, database=database)
        time.sleep(60)
    return True
