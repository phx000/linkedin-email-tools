import utils
from sending.tools import compose, send


def generate_find_replace(find_replace, database):
    out = {}

    all_data = utils.query(f"select {','.join(find_replace.values())} from leads join accounts on leads.account_fk = accounts.id where leads.id=170670", database=database)[0]

    for key, value in zip(find_replace.keys(), all_data):
        out[key] = str(value)

    out["deadline"] = "EXAMPLE DEADLINE"
    return out


def test_send(template_id, database):
    attachment_records = utils.dict_query("select id from email_attachments where email_template_fk=%s", (template_id,), database=database)
    attachment_ids = [el["id"] for el in attachment_records]
    attachments = compose.build_attachments(attachment_ids, database)

    template = utils.dict_query("select * from email_templates where id=%s", (template_id,), database=database)[0]
    template["find_replace"] = generate_find_replace(template["find_replace"], database)

    mailserver = utils.dict_query("select * from mailservers where host='bcf-info.eu' limit 1", database=database)
    send.create_smtp_connections(mailserver)

    message = compose.build_message(template, "filip.esrubio@bcf-info.eu", "filip.esrubio@bcf-info.eu", attachments)
    sending_result = mailserver[0]["conn"].sendmail("filip.esrubio@bcf-info.eu", "filip.esrubio@bcf-info.eu", message.as_bytes())
    print("Sending result:", sending_result)


if __name__ == "__main__":
    test_send(6, "hr")
