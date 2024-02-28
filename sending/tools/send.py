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


def update_ipv4(domain_record, database):
    ips = resolve_domain_to_mx_ips(domain_record["domain"])
    if not ips:
        ips = ["0"]

    conn = utils.connection(database=database)
    cursor = conn.cursor()
    for ip in ips:
        cursor.execute("insert into domain_mx_ipv4s (ipv4, domain_fk) values (%s,%s)", (ip, domain_record["id"]))
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


def get_email_template_from_campaign_part_id(campaign_part_id, database):
    message_template = utils.dict_query("""select *
                                                  from email_templates
                                                        join campaign_parts on email_templates.id = campaign_parts.email_template_fk
                                                  where campaign_parts.id=%s""", (campaign_part_id,), database=database)[0]
    return message_template


def get_latest_messages_with_same_sender_server_and_same_recipient_server(mailserver_id, recipient_ips, database):
    latest_messages = utils.dict_query("""select messages.sent_timestamp
                                                                from messages
                                                                         join addresses on messages.address_fk = addresses.id
                                                                         join domains on addresses.domain_fk = domains.id
                                                                         join domain_mx_ipv4s on domain_mx_ipv4s.domain_fk = domains.id
                                                                where messages.sent = true
                                                                  and messages.mailserver_fk =%s
                                                                  and domain_mx_ipv4s.ipv4 in %s
                                                                  and extract(epoch from (%s - messages.sent_timestamp)) < 3600
                                                                order by current_timestamp desc""",
                                       (mailserver_id, tuple(recipient_ips), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), database=database)
    return latest_messages


def build_recipient_address(address_id, database):
    username, domain = utils.query("""select addresses.username, domains.domain
                                            from addresses
                                                     join domains on addresses.domain_fk = domains.id
                                            where addresses.id =%s""", (address_id,), database=database)[0]
    return username + "@" + domain


def is_ready_for_sending(message, database):
    campaign_part_start_timestamp = utils.query("""select start_timestamp 
                                                            from messages 
                                                                join campaign_parts on messages.campaign_part_fk = campaign_parts.id 
                                                            where campaign_parts.id=%s""", (message["campaign_part_fk"],), database=database)[0][0]
    current_datetime = datetime.datetime.now()
    return current_datetime > campaign_part_start_timestamp


def send_messages(messages, database):
    print(" - Establishing SMTP connections with sender servers")
    mailservers = utils.dict_query("select * from mailservers", database=database)
    create_smtp_connections(mailservers)
    campaign_part_id_to_attachments = {}
    print(" - Success")

    # todo remove the enumerate
    for ind, message in enumerate(messages):
        print("   - Working on message number", ind)
        if not is_ready_for_sending(message, database):
            print("   - Message not ready to be sent")
            continue
        print("   - Message ready to be sent")
        print("   - Building attachments")
        message_template = get_email_template_from_campaign_part_id(message["campaign_part_fk"], database)
        if message["campaign_part_fk"] not in campaign_part_id_to_attachments:
            print(f"     - Attachments for campaign_part {message['campaign_part_fk']} not in the dict. Creating")
            attachments = get_attachments_from_campaign_part_id(message["campaign_part_fk"], database)
            campaign_part_id_to_attachments[message["campaign_part_fk"]] = attachments
        attachments = campaign_part_id_to_attachments[message["campaign_part_fk"]]

        print("   - Looking for IPs of the recipient mailservers")
        domain_record = utils.dict_query("select domains.* from messages join addresses on messages.address_fk = addresses.id join domains on addresses.domain_fk = domains.id where addresses.id=%s",
                                         (message["address_fk"],), database=database)[0]
        ips = utils.dict_query("select ipv4 from domain_mx_ipv4s where domain_fk=%s", (domain_record["id"],), database=database)
        if not ips:
            print(f"     - IPs not found in the DB, making DNS resolution for domain '{domain_record['domain']}'. Results:")
            ips = update_ipv4(domain_record, database)

        else:
            print("     - IPs found in the DB. Results:")
            ips = [el["ipv4"] for el in ips]

        # todo remove this loop
        for ip in ips:
            print(f"       - {ip}")

        print("   - Looping through sender mailservers")

        valid_mailservers = mailservers.copy()
        if message["mailserver_fk"] is not None:
            valid_mailservers = next(mailserver for mailserver in mailservers if mailserver["id"] == message["mailserver_fk"])

        for mailserver in valid_mailservers:
            print(f"     - '{mailserver['host']}'")
            current_datetime = datetime.datetime.now()
            print("       - Making latest_messages query. Results:")
            latest_messages = get_latest_messages_with_same_sender_server_and_same_recipient_server(mailserver["id"], ips, database)

            # todo remove this loop
            for mess in latest_messages:
                print(f"         - {mess}")

            if len(latest_messages) >= config.SENDING__MAX_MESSAGES_FOR_SAME_RECIPIENT_BY_SAME_SENDER_PER_HOUR:
                print("       - Overflow in number of messages/hour")
                continue

            if latest_messages:
                # timestamp_dt = datetime.datetime.strptime(latest_messages[0]["sent_timestamp"], "%Y-%m-%d %H:%M:%S")
                delta_seconds = (current_datetime - latest_messages[0]["sent_timestamp"]).total_seconds()
                if delta_seconds < config.SENDING__DELTA_TIME_BETWEEN_MESSAGES_FOR_SAME_RECIPIENT_IP:
                    print("       - Too little time before last message")
                    continue

            print("       - Building message")

            sender_address = mailserver["username"] + "@" + mailserver["host"]
            recipient_address = build_recipient_address(message["address_fk"], database)

            print("       - Sending message")

            message_object = compose.build_message(message_template, sender_address, recipient_address, attachments)
            sending_result = mailserver["conn"].sendmail(sender_address, recipient_address, message_object.as_bytes())
            print("         - RESULT:", sending_result)

            print("       - Updating record as sent")
            utils.query("update messages set sent=true, sent_timestamp=current_timestamp, mailserver_fk=%s where id=%s",
                        (mailserver["id"], message["id"],), commit=True, database=database)
            print("       - Finished with this message")
            print()
            break
