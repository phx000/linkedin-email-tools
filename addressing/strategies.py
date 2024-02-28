import utils
import clean, generate
import utils


def push_all_rr_formats_into_formats(database):
    records = utils.dict_query("select * from rocketreach where format!='-1'", database=database)
    conn = utils.connection(database)
    cursor = conn.cursor()
    for record in records:
        cursor.execute("insert into formats (account_fk, format, source) values (%s, %s, 'rr') on conflict do nothing", (record["account_fk"], record["format"]))
    conn.commit()
    conn.close()


def generate_addresses_from_all_leads(project):
    database = utils.get_database_name_from_project_id(project["id"])
    push_all_rr_formats_into_formats(database)
    all_leads_with_format = utils.dict_query(
        "select leads.first_name, leads.last_name, formats.format, leads.id as leads_id, formats.id as formats_id from leads join formats on leads.account_fk=formats.account_fk", database=database)
    addresses_dicts = []

    for lead in all_leads_with_format:
        clean_lead = clean.clean_first_and_last_name(lead["first_name"], lead["last_name"], project["addressing__words_to_remove"])
        if clean_lead is None:
            continue

        first_name, last_name = clean_lead
        format_ = lead["format"]
        new_addresses = generate.generate_addresses(first_name, last_name, format_)
        for address in new_addresses:
            new_dict = {
                "username": address[0],
                "domain": address[1],
                "leads_id": lead["leads_id"],
                "formats_id": lead["formats_id"]
            }
            if new_dict not in addresses_dicts:
                addresses_dicts.append(new_dict)

    conn = utils.connection(database)
    cursor = conn.cursor()

    all_domains = set([address["domain"] for address in addresses_dicts])
    domain_string_to_id_dict = {}

    for domain in all_domains:
        cursor.execute("insert into domains (domain) values (%s) on conflict do nothing", (domain,))
    conn.commit()

    for domain in all_domains:
        cursor.execute("select id from domains where domain=%s", (domain,))
        domain_string_to_id_dict[domain] = cursor.fetchone()[0]

    for address in addresses_dicts:
        cursor.execute("insert into addresses (username, domain_fk, lead_fk, format_fk) values (%s,%s,%s,%s) on conflict do nothing",
                       (address["username"], domain_string_to_id_dict[address["domain"]], address["leads_id"], address["formats_id"]))

    conn.commit()
    conn.close()
