import utils
from tools import send
import config
import time


# def start_campaign()

# todo filter by validation of emails, unsub, other sources.

def create_messages(campaign_part, database):
    # todo refine this query
    messages = utils.dict_query("select * from messages", database=database)
    conn = utils.connection(database)
    cursor = conn.cursor()

    for message in messages:
        cursor.execute("insert into messages (address_fk, campaign_part_fk, mailserver_fk) values (%s,%s,%s)", (message["address_fk"], campaign_part["id"], message["mailserver_fk"]))

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
        while not_sent_messages:
            send.send_messages(not_sent_messages, database)
            not_sent_messages = utils.dict_query("select * from messages where sent=false limit %s", (config.SENDING__NUMBER_OF_NOT_SENT_MESSAGES_FETCHED_PER_DB_QUERY,), database=database)
            if not not_sent_messages:
                break
            print("Sleeping for 10 secs")
            time.sleep(10)

        for campaign in campaigns_:
            next_part = utils.dict_query("select * from campaign_parts where campaign_fk=%s and status=false order by index_in_campaign limit 1", (campaign["id"],), database=database)
            if not next_part:
                print("Campaign is finished")
                utils.query("update campaigns set status=true where id=%s", (campaign["id"],), commit=True,database=database)
                continue
            next_part = next_part[0]
            # todo make function below filter, removing unsub, replied...
            create_messages(next_part, database)
            utils.query("update campaign_parts set status=true,finish_timestamp=current_timestamp where id=%s", (next_part["id"],), commit=True, database=database)
