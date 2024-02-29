import utils
from tools import send
import config
import time


# todo filter by validation of emails, unsub, other sources.

def create_messages(prev_part, next_part, database):
    messages = utils.dict_query("select messages.*, addresses.username, domains.domain from messages join addresses on messages.address_fk = addresses.id join domains on addresses.domain_fk = domains.id where campaign_part_fk=%s and sent=true", (prev_part["id"],), database=database)
    unsub = utils.query("select address from unsub_addresses", database=database)
    unsub = [el[0] for el in unsub]

    conn = utils.connection(database)
    cursor = conn.cursor()
    for message in messages:
        if message["username"]+"@"+message["domain"] not in unsub:
            cursor.execute("insert into messages (address_fk, campaign_part_fk, mailserver_fk) values (%s,%s,%s)", (message["address_fk"], next_part["id"], message["mailserver_fk"]))
    conn.commit()
    conn.close()


def simple_strategy(project):
    database = utils.get_database_name_from_project_id(project["id"])
    while True:
        campaigns_ = utils.dict_query("select * from campaigns where status=false", database=database)
        if not campaigns_:
            print("All campaigns are finished")
            return

        not_sent_messages = utils.dict_query("select * from messages where sent=false limit %s", (config.SENDING__NUMBER_OF_NOT_SENT_MESSAGES_FETCHED_PER_DB_QUERY,), database=database)
        if not_sent_messages:
            print(" - Establishing SMTP connections with sender servers")
            mailservers = utils.dict_query("select * from mailservers", database=database)
            send.create_smtp_connections(mailservers)
            print(" - Success")
        while not_sent_messages:
            send.send_messages(not_sent_messages, mailservers, database)
            not_sent_messages = utils.dict_query("select * from messages where sent=false limit %s", (config.SENDING__NUMBER_OF_NOT_SENT_MESSAGES_FETCHED_PER_DB_QUERY,), database=database)
            if not not_sent_messages:
                break
            print("Sleeping for 10 secs")
            time.sleep(10)

        for campaign in campaigns_:
            next_part = utils.dict_query("select * from campaign_parts where campaign_fk=%s and status=false order by index_in_campaign limit 1", (campaign["id"],), database=database)
            if not next_part:
                print("Campaign is finished")
                utils.query("update campaigns set status=true where id=%s", (campaign["id"],), commit=True, database=database)
                continue
            next_part = next_part[0]
            prev_part = utils.dict_query("select * from campaign_parts where campaign_fk=%s and status=true order by index_in_campaign desc limit 1", (campaign["id"],), database=database)
            prev_part = prev_part[0]
            # todo make function below filter, removing unsub, replied...
            create_messages(prev_part, next_part, database)
            utils.query("update campaign_parts set status=true,finish_timestamp=current_timestamp where id=%s", (next_part["id"],), commit=True, database=database)
