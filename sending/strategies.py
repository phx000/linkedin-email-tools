import utils
from tools import send
import config
import time
import datetime


def send_not_sent_messages(database):
    def get_not_sent_messages():
        return utils.dict_query(
            "select messages.* from messages join campaign_parts on messages.campaign_part_fk = campaign_parts.id where sent=false and current_timestamp > campaign_parts.start_timestamp limit %s",
            (config.SENDING__NUMBER_OF_NOT_SENT_MESSAGES_FETCHED_PER_DB_QUERY,), database=database)

    def get_mailserver_records_with_smtp_connections():
        print(" - Establishing SMTP connections with sender servers")
        mailservers_ = utils.dict_query("select * from mailservers", database=database)
        send.create_smtp_connections(mailservers_)
        print(" - Success")
        return mailservers_

    print(" - Looking for not sent message records")
    not_sent_messages = get_not_sent_messages()
    print(f" - Found {len(not_sent_messages)} not sent records")

    if not_sent_messages:
        mailservers = get_mailserver_records_with_smtp_connections()
        while not_sent_messages:
            send.send_messages(not_sent_messages, mailservers, database)
            not_sent_messages = get_not_sent_messages()
            if not not_sent_messages:
                break
            time.sleep(10)


def create_new_messages_from_campaign_parts(campaigns_, database):
    print(" - Looping through campaigns looking for new campaign_parts to create")
    for campaign in campaigns_:
        print(f"   - Campaign with id {campaign['id']}")
        next_part = utils.dict_query("select * from campaign_parts where campaign_fk=%s and status=false order by index_in_campaign limit 1", (campaign["id"],), database=database)
        if not next_part:
            print("     - No next part found")
            utils.query("update campaigns set status=true, finish_timestamp=current_timestamp where id=%s", (campaign["id"],), commit=True, database=database)
            continue

        print("     - Next part found")
        next_part = next_part[0]
        if datetime.datetime.now() > next_part["start_timestamp"]:
            print("     - Valid datetime to create messages")
            prev_part = utils.dict_query("select * from campaign_parts where campaign_fk=%s and status=true order by index_in_campaign desc limit 1", (campaign["id"],), database=database)
            prev_part = prev_part[0]
            create_messages(prev_part, next_part, database)
            utils.query("update campaign_parts set status=true,finish_timestamp=current_timestamp where id=%s", (next_part["id"],), commit=True, database=database)
            continue
        print("     - Invalid datetime to create messages")


def create_messages(prev_part, next_part, database):
    def get_prev_messages():
        return utils.dict_query(
            "select messages.*, addresses.username, domains.domain from messages join addresses on messages.address_fk = addresses.id join domains on addresses.domain_fk = domains.id where campaign_part_fk=%s and sent=true",
            (prev_part["id"],), database=database)

    def get_unsubscribed_addresses():
        addresses = utils.query("select address from unsub_addresses", database=database)
        return [el[0] for el in addresses]

    messages = get_prev_messages()
    unsubscribed = get_unsubscribed_addresses()

    conn = utils.connection(database)
    cursor = conn.cursor()
    for message in messages:
        if message["username"] + "@" + message["domain"] not in unsubscribed:
            cursor.execute("insert into messages (address_fk, campaign_part_fk, mailserver_fk) values (%s,%s,%s)", (message["address_fk"], next_part["id"], message["mailserver_fk"]))
    conn.commit()
    conn.close()


def create_new_campaign_with_available_addresses(database):
    def get_next_week_weekday(date, weekday_index):
        days_to_add = 6 - date.weekday() + weekday_index + 1
        return date + datetime.timedelta(days=days_to_add)

    def format_date(date):
        remainder = date.day % 10
        if 1 <= remainder <= 3:
            termination = ["st", "nd", "rd"][remainder - 1]
        else:
            termination = "th"
        return f"{date.strftime('%B')} {date.day}{termination}"

    def get_reminder_sending_date(date):
        day_after_7_days = date + datetime.timedelta(days=7)
        next_weeks_thursday_at_6_am = get_next_week_weekday(date, 3).replace(hour=6, minute=0, second=0)
        return min(day_after_7_days, next_weeks_thursday_at_6_am)

    available_addresses = utils.dict_query(
        "select addresses.* from addresses left join messages on addresses.id = messages.address_fk where messages.address_fk is null and addresses.validation in ('ok','catch_all','unknown')",
        database=database)

    if not available_addresses:
        print(" - No addresses to use")
        return

    conn = utils.connection(database)
    cursor = conn.cursor()

    cursor.execute("insert into campaigns default values returning id")
    campaign_id = cursor.fetchone()[0]

    deadline = format_date(get_next_week_weekday(datetime.datetime.now(), 4))
    reminder_sending_date = get_reminder_sending_date(datetime.datetime.now())

    cursor.execute("""insert into campaign_parts
                        (email_template_fk, campaign_fk, start_timestamp, index_in_campaign, deadline)
                        values (5, %s, current_timestamp, 1, %s), (6, %s, %s, 2, %s) returning id""", (campaign_id, deadline, campaign_id, reminder_sending_date, deadline))

    first_campaign_part_id = cursor.fetchone()[0]

    for address in available_addresses:
        cursor.execute("insert into messages (address_fk, campaign_part_fk) VALUES (%s,%s)", (address["id"], first_campaign_part_id))

    conn.commit()
    conn.close()

    print(f" - New campaign created with id {campaign_id}")
