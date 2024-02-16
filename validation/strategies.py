import validate
import utils
import time


def simple_validation(project):
    print("Getting emails to validate")
    database = utils.get_database_name_from_project_id(project["id"])
    result = validate.upload_all_non_validated_emails_for_validation(database)
    if result == -2:
        print("  No emails to validate")
    if result == -1:
        print("  Error uploading new emails for validation")

    time.sleep(5)

    print("Looking for not fetched files")
    while True:
        result = validate.fetch_all_not_fetched_validation_files(database)
        if result is None:
            print("  All is fetched")
            print("Finished")
            return
        print("  Files left to fetch. Not ready yet. Sleeping 300s")
        time.sleep(100)
