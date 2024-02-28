import utils
import imaplib
from tools import imap, website


def default_strategy(project):
    database = utils.get_database_name_from_project_id(project["id"])
    folders_1 = ["INBOX", "Archive", "PA", "PA Archive"]
    folders_2 = ["Answers", "Answers/Interested", "Not able+no interest", "Unsubscribe"]
    all_folders = [f"\"{folder_1}/" + folder_2 + "\"" for folder_1 in folders_1 for folder_2 in folders_2]

    mailservers = utils.dict_query("select * from mailservers", database=database)
    all_from_addresses = set()

    for mailserver in mailservers:
        print(f" - Working on {mailserver['host']}")
        conn = imaplib.IMAP4_SSL(mailserver["host"])
        conn.login(mailserver["username"] + "@" + mailserver["host"], mailserver["password"])
        all_from_addresses.update(imap.fetch_all_addresses_from_folders(conn, all_folders))

    conn = utils.connection(database)
    cursor = conn.cursor()
    cursor.executemany("insert into unsub_addresses (address) values (%s) on conflict do nothing", tuple((address,) for address in all_from_addresses))
    conn.commit()
    conn.close()
