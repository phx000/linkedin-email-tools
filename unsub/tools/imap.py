import utils
import imaplib
import email
import re


def fetch_all_addresses_from_folder(conn, folder):
    pattern = r'<(.*?)>'
    from_addresses = set()

    result, data = conn.select(folder)
    if result != 'OK':
        return set()

    result, data = conn.search(None, 'ALL')

    if result == 'OK':
        email_ids = data[0].split()
        for email_id in email_ids:
            result, data = conn.fetch(email_id, '(RFC822)')
            if result == 'OK':
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                from_address = re.findall(pattern, msg['From'].lower().strip())
                from_addresses.update(set(from_address))

    return from_addresses


def fetch_all_addresses_from_folders(conn, folders):
    from_addresses = set()
    for folder in folders:
        print(f"   - {folder}")
        from_addresses.update(fetch_all_addresses_from_folder(conn, folder))
    return from_addresses
