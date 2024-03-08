import utils
import config
import smtplib
import datetime
import dns.resolver
from . import compose


def create_smtp_connections(records):
    for record in records:
        record["conn"] = smtplib.SMTP("mail." + record["host"], 587)
        record["conn"].starttls()
        record["conn"].login(record["username"] + "@" + record["host"], record["password"])


def resolve_domain_to_mx_ips(domain):
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_ips = []
        for record in mx_records:
            a_records = dns.resolver.resolve(record.exchange, 'A')
            for a_record in a_records:
                mx_ips.append(a_record.address)
        return mx_ips
    except dns.resolver.NoAnswer:
        return []
    except dns.resolver.NXDOMAIN:
        return []


def insert_ipv4s(domain_record, database):
    ips = resolve_domain_to_mx_ips(domain_record["domain"])
    if not ips:
        ips = ["0"]

    conn = utils.connection(database=database)
    cursor = conn.cursor()

    data_string = ','.join([str(t) for t in [(ip, domain_record["id"]) for ip in ips]])
    cursor.execute("insert into domain_mx_ipv4s (ipv4, domain_fk) values %s" % data_string)

    conn.commit()
    conn.close()
    return None if ips == ["0"] else ips


def get_attachments_from_campaign_part_id(campaign_part_id, database):
    attachment_ids = utils.query("""select distinct email_attachments.id
                                            from messages
                                                     join campaign_parts on messages.campaign_part_fk = campaign_parts.id
                                                     join email_templates on campaign_parts.email_template_fk = email_templates.id
                                                     join email_attachments on email_templates.id = email_attachments.email_template_fk
                                            where campaign_parts.id =%s""", (campaign_part_id,), database=database)
    attachment_ids = [el[0] for el in attachment_ids]
    return compose.build_attachments(attachment_ids, database)




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


def build_recipient_address(address_id, database):
    username, domain = utils.query("""select addresses.username, domains.domain
                                            from addresses
                                                     join domains on addresses.domain_fk = domains.id
                                            where addresses.id =%s""", (address_id,), database=database)[0]
    return username + "@" + domain


def send_messages(messages, mailservers, database):
    def get_template(campaign_part_id):
        return utils.dict_query("""select *
                                          from email_templates
                                                join campaign_parts on email_templates.id = campaign_parts.email_template_fk
                                          where campaign_parts.id=%s""", (campaign_part_id,), database=database)[0]

    def get_attachments():
        if message["campaign_part_fk"] not in campaign_part_id__attachments:
            attachments = get_attachments_from_campaign_part_id(message["campaign_part_fk"], database)
            campaign_part_id__attachments[message["campaign_part_fk"]] = attachments
        return campaign_part_id__attachments[message["campaign_part_fk"]]

    def get_ips():
        domain_record = utils.dict_query("""select domains.*
                                                    from messages
                                                             join addresses on messages.address_fk = addresses.id
                                                             join domains on addresses.domain_fk = domains.id
                                                    where addresses.id =%s""",
                                         (message["address_fk"],), database=database)[0]
        ips = utils.query("select ipv4 from domain_mx_ipv4s where domain_fk=%s", (domain_record["id"],), database=database)

        if ips:
            return [el[0] for el in ips]
        else:
            return insert_ipv4s(domain_record, database)

    def get_find_replace_data():
        return utils.dict_query("""select leads.first_name, accounts.name as company, campaign_parts.deadline
                                            from messages
                                                     join addresses on messages.address_fk = addresses.id
                                                     join leads on addresses.lead_fk = leads.id
                                                     join accounts on leads.account_fk = accounts.id
                                                     join campaign_parts on messages.campaign_part_fk = campaign_parts.id
                                            where addresses.id =%s""", (message["address_fk"],), database=database)[0]

    campaign_part_id__attachments = {}

    print(f" - {len(messages)} messages left to send")

    for message in messages:
        ips = get_ips()

        valid_mailservers = mailservers.copy()
        if message["mailserver_fk"] is not None:
            valid_mailservers = [next(mailserver for mailserver in mailservers if mailserver["id"] == message["mailserver_fk"])]

        for mailserver in valid_mailservers:
            current_datetime = datetime.datetime.now()
            latest_messages = get_latest_messages_with_same_sender_server_and_same_recipient_server(mailserver["id"], ips, database)

            if len(latest_messages) >= config.SENDING__MAX_MESSAGES_FOR_SAME_RECIPIENT_BY_SAME_SENDER_PER_HOUR:
                continue

            if latest_messages:
                delta_seconds = (current_datetime - latest_messages[0]["sent_timestamp"]).total_seconds()
                if delta_seconds < config.SENDING__DELTA_TIME_BETWEEN_MESSAGES_FOR_SAME_RECIPIENT_IP:
                    continue

            message_template = get_template(message["campaign_part_fk"])
            find_replace_data = get_find_replace_data()
            sender_address = mailserver["username"] + "@" + mailserver["host"]
            recipient_address = build_recipient_address(message["address_fk"], database)
            attachments = get_attachments()

            message_object = compose.build_message(message_template, find_replace_data, sender_address, recipient_address, attachments)
            sending_result = mailserver["conn"].sendmail(sender_address, recipient_address, message_object.as_bytes())

            if sending_result != {}:
                raise Exception("Sending result is not {}")

            print(f"   - Sent message with id {message['id']} at {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

            utils.query("update messages set sent=true, sent_timestamp=current_timestamp, mailserver_fk=%s, smtp_id=%s where id=%s",
                        (mailserver["id"], message_object["Message-ID"], message["id"],), commit=True, database=database)
            break
