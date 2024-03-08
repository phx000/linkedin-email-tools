import utils
from tools import imap, parse, clean
from email.parser import BytesParser
import time


def simple_strategy(mailservers, project):
    database = utils.get_database_name_from_project_id(project["id"])
    all_remaining_messages = utils.dict_query(
        "select messages.id as id,messages.smtp_id as smtp_id from messages left join message_analytics on messages.id = message_analytics.message_fk where message_analytics.message_fk is null",
        database=database)
    smtp_id__id_dict = {message["smtp_id"]: message["id"] for message in all_remaining_messages}

    for mailserver in mailservers:
        print(f"   - Working on {mailserver['host']}")
        conn = mailserver["conn"]
        conn.select("INBOX")
        _, message_ids = conn.search(None, "ALL")
        message_ids = message_ids[0].split()

        print(f"     - Performing analysis")
        for message_id in message_ids:
            print(f"       - Message {message_id.decode()}/{len(message_ids)}")

            while True:
                res, message_bytes = conn.fetch(message_id, "(BODY.PEEK[HEADER])")
                if res == "OK":
                    message = BytesParser().parsebytes(message_bytes[0][1])
                    break
                time.sleep(0.1)

            message_fk = None
            headers_to_search = ["In-Reply-To", "References"]

            for header_to_search in headers_to_search:
                if header_to_search in message:
                    ids = parse.separate_message_ids(message[header_to_search])
                    for id_ in ids:
                        if id_ in smtp_id__id_dict.keys():
                            message_fk = smtp_id__id_dict[id_]
                            break
                    if message_fk is not None:
                        break

            if message_fk is None:
                continue

            content_type = None
            if "Content-Type" in message:
                if ";" in message["Content-Type"]:
                    content_type = message["Content-Type"][:message["Content-Type"].find(";")].strip()
                else:
                    content_type = message["Content-Type"].strip()

            auto_submitted = message["Auto-Submitted"] if "Auto-Submitted" in message else None

            subject = None
            if "Subject" in message:
                subject = parse.decode_subject(message["Subject"])

            print(f"         - Added with message_fk {message_fk}")

            utils.query("insert into message_analytics (message_fk, content_type, auto_submitted, subject) values (%s,%s,%s,%s) on conflict do nothing",
                        (message_fk, content_type, auto_submitted, subject), commit=True, database=database)

        conn.select("INBOX")

        print(f"     - Moving")
        for substring in ["auto", "read", "gelesen", "non lu"]:
            clean.move_emails(conn, substring, "INBOX/Read+Auto")

        print(f"     - Deleting")
        for substring in ["deliv", "return", "warning", "delayed", "report", "failure", "aviso:"]:
            clean.delete_emails(conn, substring)

        conn.expunge()
        break
