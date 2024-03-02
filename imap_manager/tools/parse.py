import re
from email.header import decode_header


def separate_message_ids(references_header):
    pattern = r'(<[^<>]+>)'
    message_ids = re.findall(pattern, references_header)
    return message_ids


def decode_subject(encoded_subject):
    decoded_parts = []
    for part, encoding in decode_header(encoded_subject):
        if isinstance(part, bytes):
            decoded_parts.append(part.decode(encoding or 'ascii'))
        else:
            decoded_parts.append(part)

    decoded_subject = ''.join(decoded_parts)
    return decoded_subject
