import validate
import utils
import time


def find_all_non_fetched_validation_files(project):
    print("Looking for not fetched files")
    database=utils.get_database_name_from_project_id(project["id"])
    while True:
        result = validate.fetch_all_not_fetched_validation_files(database)
        if result is None:
            print("  Nothing to fetch")
            return
        print("  Files left to fetch. Not ready yet. Sleeping 100s")
        time.sleep(100)


def validation_upload_all_possible(project):
    print("Getting emails to validate")
    database = utils.get_database_name_from_project_id(project["id"])
    result = validate.upload_all_non_validated_emails_for_validation(database)
    if result == -2:
        print("  No emails to validate")
    if result == -1:
        print("  Error uploading new emails for validation")

    time.sleep(5)
