import utils
import requests
import csv
import config
import datetime


def upload_emails_for_validation(records, api_key, database):
    csv_header = "id,emails"
    build_address = lambda x: x["username"] + "@" + x["domain"]
    csv_body = "\n".join([",".join([str(record["id"]), build_address(record)]) for record in records])
    csv_string = csv_header + "\n" + csv_body

    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    file_name = f"{database} {formatted_datetime}.csv"

    files = {'file_contents': (file_name, csv_string)}
    data = {"key": api_key}
    url = "https://bulkapi.millionverifier.com/bulkapi/v2/upload"
    response = requests.post(url, files=files, data=data)

    if response.status_code != 200:
        print("MillionVerified bulk API returned bad HTTP code:", response.status_code)
        return

    try:
        response = response.json()
    except requests.JSONDecodeError:
        print("MillionVerified bulk API response is not JSON")
        return

    if "file_id" not in response:
        print("MillionVerified bulk API returned JSON with no 'file_id'")
        return

    conn = utils.connection(database=database)
    cursor = conn.cursor()
    for record in records:
        cursor.execute("update addresses set validation='validating' where id=%s", (record["id"],))
    conn.commit()
    conn.close()

    return response


def upload_all_non_validated_emails_for_validation(database):
    addresses = utils.dict_query("select addresses.*, domains.domain from addresses join domains on addresses.domain_fk = domains.id where validation is null", database=database)
    if not addresses:
        return -2

    result = upload_emails_for_validation(addresses, config.VALIDATION__MILLIONVERIFIER_API_KEY, database)
    if result is None:
        return -1

    utils.query("insert into validation (mv_id) values (%s)", (result["file_id"],), commit=True, database=database)
    return 1


def check_validation_status_from_file_id(file_id, api_key):
    url = f"https://bulkapi.millionverifier.com/bulkapi/v2/fileinfo"
    params = {"key": api_key, "file_id": file_id}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("MillionVerified bulk API returned bad HTTP code:", response.status_code)
        return

    try:
        response = response.json()
    except requests.JSONDecodeError:
        print("MillionVerified bulk API response is not JSON")
        return

    if "error" in response and response["error"]:
        print("Error field in json response:", response["error"])

    if "status" not in response:
        print("Status key not in json response")
        return

    if response["status"] == "canceled":
        print("File status is 'canceled'")
        return

    if response["status"] == "finished":
        return True

    return False


def csv_bytes_to_dicts(bytes_):
    string = bytes_.decode("utf8")
    lines = string.splitlines()
    reader = csv.DictReader(lines)
    return list(reader)


def update_records_with_results(dicts, database):
    utils.dicts_commit("update addresses set validation=%s where id=%s", ("result", "id"), dicts, database=database)


def fetch_results_from_file_id(file_id, api_key):
    url = f"https://bulkapi.millionverifier.com/bulkapi/v2/download"
    params = {"key": api_key, "file_id": file_id, "filter": "all"}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("MillionVerified bulk API returned bad HTTP code:", response.status_code)
        return

    return csv_bytes_to_dicts(response.content)


def fetch_all_not_fetched_validation_files(database):
    not_fetched_files = utils.dict_query("select * from validation where status=false", database=database)
    if not not_fetched_files:
        print("Nothing to fetch")
        return

    for file in not_fetched_files:
        print(f"  Working on file psql_id {file['id']} mv_id {file['mv_id']}")
        is_file_ready_to_fetch = check_validation_status_from_file_id(file["mv_id"], config.VALIDATION__MILLIONVERIFIER_API_KEY)
        if is_file_ready_to_fetch:
            result = fetch_results_from_file_id(file["mv_id"], config.VALIDATION__MILLIONVERIFIER_API_KEY)
            if result is not None:
                update_records_with_results(result, database)
                utils.query("update validation set status=true,finish_timestamp=current_timestamp where id=%s", (file["id"],), commit=True, database=database)

    not_fetched_files = utils.dict_query("select * from validation where status=false", database=database)
    if not not_fetched_files:
        return

    return True
