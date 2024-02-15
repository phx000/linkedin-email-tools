import utils
import clean, generate, _specifics


# def insert_new_addresses(addresses, database):
#     conn = utils.connection(database)
#     cursor = conn.cursor()
#     for address in addresses:
#         cursor.execute("insert into addresses (address, lead_fk, format_fk) values (%s,%s,%s)",(address["add"]))

# first name, last name, format, lead.id, format.id
def generate_addresses_from_all_leads(project):
    database = utils.get_database_name_from_project_id(project["id"])
    all_leads_with_format = utils.dict_query("select leads.first_name, leads.last_name, formats.format, leads.id as leads_id, formats.id as formats_id from leads join formats on leads.account_fk=formats.account_fk", database=database)
    conn = utils.connection(database)
    cursor = conn.cursor()

    for lead in all_leads_with_format:
        clean_lead = clean.clean_first_and_last_name(lead["first_name"], lead["last_name"], _specifics.words)
        if clean_lead is None:
            continue

        first_name, last_name = clean_lead
        format_ = lead["format"]
        new_addresses = generate.generate_addresses(first_name, last_name, format_)

        for new_address in new_addresses:
            cursor.execute("insert into addresses (address, lead_fk, format_fk) values (%s,%s,%s) on conflict do nothing",(new_address, lead["leads_id"], lead["formats_id"]))

    conn.commit()
    conn.close()


# def generate_all_possible(project):
#     all_people = utils.dict_query("select first_name, last_name, account_fk from leads")
#     if not all_people:
#         return -2
#
#     formats = utils.dict_query("select * from formats")
#     formats_dict = {record["account_fk"]: record for record in formats}
#     addresses=set()
#
#     for person in all_people:
#         if person["account_fk"] not in formats_dict:
#             continue
#
#         clean_person = clean.clean_first_and_last_name(person["first_name"], person["last_name"], _specifics.words)
#         if clean_person is None:
#             continue
#
#         first, last = clean_person
#         format_ = formats_dict[person["account_fk"]]["format"]
#         new_addresses = generate.generate_addresses(first, last, format_)
#         addresses.update(new_addresses)
#
#     database=utils.get_database_name_from_project_id(project["id"])
#     conn=utils.connection(database)
#     cursor=conn.cursor()
#     for address in addresses:
#         cursor.execute("insert into addresses")
