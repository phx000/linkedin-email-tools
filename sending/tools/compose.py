from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64
import utils
import base64


def build_attachments(attachment_ids, database):
    attachments = []
    for attachment_id in attachment_ids:
        record = utils.dict_query("select * from email_attachments where id=%s", (attachment_id,), database=database)[0]
        new_attachment = MIMEBase(record["main_type"], record["sub_type"])
        new_attachment.set_payload(base64.b64decode(record["payload"]))
        encode_base64(new_attachment)
        if record["content_disposition"] is not None:
            new_attachment.add_header("Content-Disposition", record["content_disposition"], filename=record["name"])
        if record["content_id"] is not None:
            new_attachment.add_header("Content-ID", record["content_id"])
        attachments.append(new_attachment)
    return attachments


def build_message(template, sender_address, recipient_address, attachments):
    if template["find_replace"] is not None:
        for pair in template["find_replace"]:
            find_string = "{{" + pair["find"] + "}}"
            template["subject"] = template["subject"].replace(find_string, pair["replace"])
            template["plain"] = template["plain"].replace(find_string, pair["replace"])
            template["html"] = template["html"].replace(find_string, pair["replace"])

    message = MIMEMultipart()
    message["From"] = sender_address
    message["To"] = recipient_address
    message["Subject"] = template["subject"]

    plain = MIMEBase("text", "plain")
    plain.set_payload(template["plain"].encode())
    message.attach(plain)

    html = MIMEBase("text", "html")
    html.set_payload(template["html"].encode())
    message.attach(html)

    if attachments:
        message.set_type('multipart/mixed')
        for attachment in attachments:
            message.attach(attachment)
    else:
        message.set_type('multipart/alternative')

    return message
