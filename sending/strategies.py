import utils
from tools import send, networking
import config
import time
import datetime


def send_not_sent_messages(database):
    def get_not_sent_messages():
        return utils.dict_query("""  select messages.id             as messages__id,
                                                   messages.mailserver_fk  as messages__mailserver_fk,
                                                   addresses.id            as addresses__id,
                                                   addresses.username      as addresses__username,
                                                   domains.id              as domains__id,
                                                   domains.domain          as domains__domain,
                                                   leads.first_name        as leads__first_name,
                                                   leads.last_name         as leads__last_name,
                                                   accounts.name           as accounts__name,
                                                   campaign_parts.id       as campaign_parts__id,
                                                   campaign_parts.deadline as campaign_parts__deadline,
                                                   email_templates.id      as email_templates__id,
                                                   email_templates.subject as email_templates__subject,
                                                   email_templates.plain   as email_templates__plain,
                                                   email_templates.html    as email_templates__html
                                            from messages
                                                     join addresses on messages.address_fk = addresses.id
                                                     join domains on addresses.domain_fk = domains.id
                                                     join leads on addresses.lead_fk = leads.id
                                                     join accounts on leads.account_fk = accounts.id
                                                     join campaign_parts on messages.campaign_part_fk = campaign_parts.id
                                                     join email_templates on campaign_parts.email_template_fk = email_templates.id
                                            where messages.sent = false
                                              and current_timestamp > campaign_parts.start_timestamp
                                              and addresses.username || '@' || domains.domain not in (select address from unsub_addresses)
                                              and domains.domain not in (select domain from unsub_domains) limit %s
                                            """, (config.SENDING__NUMBER_OF_NOT_SENT_MESSAGES_FETCHED_PER_DB_QUERY,), database=database)

    def get_mailserver_records_with_smtp_connections():
        mailservers_ = utils.dict_query("select * from mailservers", database=database)
        networking.create_smtp_connections(mailservers_)
        return mailservers_

    not_sent_messages = get_not_sent_messages()

    if not not_sent_messages:
        return

    mailservers = get_mailserver_records_with_smtp_connections()
    while not_sent_messages:
        send.send_messages(not_sent_messages, mailservers, database)
        not_sent_messages = get_not_sent_messages()
        if not not_sent_messages:
            break
        time.sleep(20)


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
        next_weeks_thursday_at_6_am = get_next_week_weekday(date, 3).replace(hour=6, minute=0, second=0, microsecond=0)
        return min(day_after_7_days, next_weeks_thursday_at_6_am)

    available_addresses = utils.dict_query(
        "select addresses.* from addresses left join messages on addresses.id = messages.address_fk where messages.address_fk is null and addresses.validation in ('ok','catch_all','unknown')",
        database=database)

    if not available_addresses:
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

    campaign_part_ids = [el[0] for el in cursor.fetchall()]

    available_addresses_tuples = []
    for address in available_addresses:
        available_addresses_tuples.append((address["id"], campaign_part_ids[0]))
        available_addresses_tuples.append((address["id"], campaign_part_ids[1]))

    slices = [available_addresses_tuples[i:i + 5000] for i in range(0, len(available_addresses_tuples), 5000)]

    for slice_ in slices:
        string_slice = ','.join([str(t) for t in slice_])
        cursor.execute("insert into messages (address_fk, campaign_part_fk) values %s" % string_slice)

    conn.commit()
    conn.close()
