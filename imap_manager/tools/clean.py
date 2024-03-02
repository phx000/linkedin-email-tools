import imaplib


def delete_emails(conn, substring):
    _, search_result = conn.search(None, f'(SUBJECT {substring})')
    email_ids = search_result[0].split()

    for email_id in email_ids:
        conn.store(email_id, '+FLAGS', '\\Deleted')

    return len(email_ids)


def move_emails(conn, substring, destination):
    _, search_result = conn.search(None, f'(SUBJECT "{substring}")')
    email_ids = search_result[0].split()

    for email_id in email_ids:
        conn.copy(email_id, destination)
        conn.store(email_id, '+FLAGS', '\\Deleted')

    return len(email_ids)
