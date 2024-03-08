import utils
import imaplib


def create_imap_connections(records):
    for record in records:
        conn = imaplib.IMAP4("mail." + record["host"])
        conn.starttls()
        conn.login(record["username"] + "@" + record["host"], record["password"])
        record["conn"] = conn


# def query_message(conn, mbox_id, query):
#     _, raw_data = conn.fetch(mbox_id, query)
#     return raw_data[0][1]
