import utils
import clean, generate
import utils
import time


def push_all_rr_formats_into_formats(database):
    records = utils.dict_query("select * from rocketreach where format!='-1'", database=database)
    conn = utils.connection(database)
    cursor = conn.cursor()
    for record in records:
        cursor.execute("insert into formats (account_fk, format, source) values (%s, %s, 'rr') on conflict do nothing", (record["account_fk"], record["format"]))
    conn.commit()
    conn.close()


def generate_addresses_from_all_non_used_leads(project):
    database = utils.get_database_name_from_project_id(project["id"])
    push_all_rr_formats_into_formats(database)

    all_leads_with_format = utils.dict_query("""select leads.first_name, leads.last_name, formats.format, leads.id as leads_id, formats.id as formats_id
                                                            from leads
                                                                     left join addresses on leads.id = addresses.lead_fk
                                                                     join formats on leads.account_fk = formats.account_fk
                                                            where addresses.lead_fk is null""", database=database)
    addresses_dicts = []

    for ind,lead in enumerate(all_leads_with_format):
        clean_lead = clean.clean_first_and_last_name(lead["first_name"], lead["last_name"])
        if clean_lead is None:
            continue

        first_name, last_name = clean_lead
        new_addresses = generate.generate_addresses(first_name, last_name, lead["format"])
        for address in new_addresses:
            new_dict = {
                "username": address[0],
                "domain": address[1],
                "leads_id": lead["leads_id"],
                "formats_id": lead["formats_id"]
            }
            addresses_dicts.append(new_dict)

    conn = utils.connection(database)
    cursor = conn.cursor()

    all_domains = set(address["domain"] for address in addresses_dicts)

    cursor.execute("insert into domains (domain) values %s on conflict do nothing" % ",".join("('" + domain + "')" for domain in all_domains))
    conn.commit()

    cursor.execute("select id, domain from domains")
    domain__id = {el[1]: el[0] for el in cursor.fetchall()}

    addresses_data = ((address["username"], domain__id[address["domain"]], address["leads_id"], address["formats_id"]) for address in addresses_dicts)
    cursor.execute("insert into addresses (username, domain_fk, lead_fk, format_fk) values %s on conflict do nothing" % ",".join(str(el) for el in addresses_data))

    conn.commit()
    conn.close()
