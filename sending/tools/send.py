import utils
import config
from . import networking
import datetime
from . import compose


def insert_ipv4s(domain_string, domain_id, database):
    ips = networking.resolve_domain_to_mx_ips(domain_string)
    if not ips:
        ips = ["0"]

    conn = utils.connection(database=database)
    cursor = conn.cursor()

    data_string = ','.join([str(t) for t in [(ip, domain_id) for ip in ips]])
    cursor.execute("insert into domain_mx_ipv4s (ipv4, domain_fk) values %s" % data_string)

    conn.commit()
    conn.close()
    return None if ips == ["0"] else ips


def get_latest_messages_with_same_sender_server_and_same_recipient_server(mailserver_id, recipient_ips, database):
    latest_messages = utils.dict_query("""select distinct(messages.sent_timestamp)
                                                                from messages
                                                                         join addresses on messages.address_fk = addresses.id
                                                                         join domains on addresses.domain_fk = domains.id
                                                                         join domain_mx_ipv4s on domain_mx_ipv4s.domain_fk = domains.id
                                                                where messages.sent = true
                                                                  and messages.mailserver_fk =%s
                                                                  and domain_mx_ipv4s.ipv4 in %s
                                                                  and extract(epoch from (%s - messages.sent_timestamp)) < 3600
                                                                order by sent_timestamp desc""",
                                       (mailserver_id, tuple(recipient_ips), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), database=database)
    return latest_messages


def send_messages(messages, mailservers, database):
    def get_ips():
        ips = utils.query("select ipv4 from domain_mx_ipv4s where domain_fk=%s", (message["addresses__id"],), database=database)

        if ips:
            return [el[0] for el in ips]
        else:
            return insert_ipv4s(message["domains__domain"], message["domains__id"], database)

    def get_attachments():
        attachment_records = utils.dict_query("select * from email_attachments where email_template_fk=%s", (message["email_templates__id"],), database=database)
        return compose.build_attachments(attachment_records, database)

    campaign_part_id__attachments = {}

    print(f" - {len(messages)} messages left to send")

    for message in messages:
        ips = get_ips()

        message_template = {
            "subject": message["email_templates__subject"],
            "plain": message["email_templates__plain"],
            "html": message["email_templates__html"]
        }

        find_replace_data = {
            "first_name": message["leads__first_name"],
            "last_name": message["leads__last_name"],
            "company": message["accounts__name"],
            "deadline": message["campaign_parts__deadline"]
        }

        if message["campaign_parts__id"] not in campaign_part_id__attachments:
            attachments = get_attachments()
            message["campaign_parts__id"]=attachments
        attachments=message["campaign_parts__id"]

        valid_mailservers = mailservers.copy()
        if message["messages__mailserver_fk"] is not None:
            valid_mailservers = [next(mailserver for mailserver in mailservers if mailserver["id"] == message["messages__mailserver_fk"])]

        for mailserver in valid_mailservers:
            current_datetime = datetime.datetime.now()
            latest_messages = get_latest_messages_with_same_sender_server_and_same_recipient_server(mailserver["id"], ips, database)

            if len(latest_messages) >= config.SENDING__MAX_MESSAGES_FOR_SAME_RECIPIENT_BY_SAME_SENDER_PER_HOUR:
                continue

            if latest_messages:
                delta_seconds = (current_datetime - latest_messages[0]["sent_timestamp"]).total_seconds()
                if delta_seconds < config.SENDING__DELTA_TIME_BETWEEN_MESSAGES_FOR_SAME_RECIPIENT_IP:
                    continue

            sender_address = mailserver["username"] + "@" + mailserver["host"]
            recipient_address = message["addresses__username"] + "@" + message["domains__domain"]

            message_object = compose.build_message(message_template, find_replace_data, sender_address, recipient_address, attachments)
            sending_result = mailserver["conn"].sendmail(sender_address, recipient_address, message_object.as_bytes())

            if sending_result != {}:
                raise Exception("Sending result is not {}")

            print(f"   - Sent message with id {message['messages__id']} at {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

            utils.query("update messages set sent=true, sent_timestamp=current_timestamp, mailserver_fk=%s, smtp_id=%s where id=%s",
                        (mailserver["id"], message_object["Message-ID"], message["messages__id"],), commit=True, database=database)
            break
