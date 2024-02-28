import utils


def add_from_txt_file(path, database):
    with open(path, "r", encoding="utf8") as file:
        raw_addresses = file.read().splitlines()

    clean_addresses = set()
    for address in raw_addresses:
        address = address.strip()
        if "@" in address and "." in address:
            clean_addresses.add(address.lower())
    clean_addresses = tuple((clean_address,) for clean_address in clean_addresses)

    conn = utils.connection(database)
    cursor = conn.cursor()
    cursor.executemany("insert into unsub_addresses (address) values (%s) on conflict do nothing", clean_addresses)
    conn.commit()
    conn.close()
