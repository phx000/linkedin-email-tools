from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64
from email.utils import make_msgid
from addressing import clean
import utils
import base64


# def build_attachments(attachment_ids, database):
#     attachments = []
#     for attachment_id in attachment_ids:
#         record = utils.dict_query("select * from email_attachments where id=%s", (attachment_id,), database=database)[0]
#         new_attachment = MIMEBase(record["main_type"], record["sub_type"])
#         new_attachment.set_payload(base64.b64decode(record["payload"]))
#         encode_base64(new_attachment)
#         if record["content_disposition"] is not None:
#             new_attachment.add_header("Content-Disposition", record["content_disposition"], filename=record["name"])
#         if record["content_id"] is not None:
#             new_attachment.add_header("Content-ID", record["content_id"])
#         attachments.append(new_attachment)
#     return attachments

def build_attachments(attachment_records, database):
    attachments = []
    for attachment in attachment_records:
        new_attachment = MIMEBase(attachment["main_type"], attachment["sub_type"])
        new_attachment.set_payload(base64.b64decode(attachment["payload"]))
        encode_base64(new_attachment)
        if attachment["content_disposition"] is not None:
            new_attachment.add_header("Content-Disposition", attachment["content_disposition"], filename=attachment["name"])
        if attachment["content_id"] is not None:
            new_attachment.add_header("Content-ID", attachment["content_id"])
        attachments.append(new_attachment)
    return attachments


def replace_placeholders(text, data):
    if "{{first_name}}" in text:
        clean_first_name = clean.clean_first_name(data["first_name"]).title()
        text = text.replace("{{first_name}}", clean_first_name)
    text = text.replace("{{company}}", data["company"])
    text = text.replace("{{deadline}}", data["deadline"])
    return text


def build_message(template, find_replace_data, sender_address, recipient_address, attachments):
    template["subject"] = replace_placeholders(template["subject"], find_replace_data)
    template["plain"] = replace_placeholders(template["plain"], find_replace_data)
    template["html"] = replace_placeholders(template["html"], find_replace_data)

    message = MIMEMultipart()
    message["From"] = sender_address
    message["To"] = recipient_address
    message["Subject"] = template["subject"]
    message["Message-ID"] = make_msgid(domain=sender_address.split("@")[1])

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
