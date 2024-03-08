import utils
import json


def add_biggest_companies(country_id, country_name, down_to_letter, project):
    letters = "IHGFEDCB"
    letters_to_use = letters[:letters.find(down_to_letter) + 1]
    for letter in letters_to_use:
        filters = {
            "spell_check": False,
            "filters": [
                {
                    "type": "Region",
                    "values_type": "values_list",
                    "values": [
                        {
                            "type": "id",
                            "_text": country_name,
                            "value": country_id
                        }
                    ]
                },
                {
                    "type": "CompanyHeadcount",
                    "values_type": "values_list",
                    "values": [
                        {
                            "type": "id",
                            "value": letter
                        }
                    ]
                }
            ]
        }

        utils.query("""insert into requests 
                    (type, data, data_children, start, project, status) values
                    (false, %s, %s, 0, %s, 0)""", (json.dumps(filters), json.dumps([]), project["id"]), commit=True)


project = utils.dict_query("select * from projects where name='pa'")[0]

data = [{"name": "Albania", "id": "102845717", "lowest_letter": "C"}, {"name": "Andorra", "id": "106296266", "lowest_letter": "B"}, {"name": "Austria", "id": "103883259", "lowest_letter": "D"},
        {"name": "Belarus", "id": "101705918", "lowest_letter": "C"}, {"name": "Belgium", "id": "100565514", "lowest_letter": "E"},
        {"name": "Bosnia and Herzegovina", "id": "102869081", "lowest_letter": "C"}, {"name": "Bulgaria", "id": "105333783", "lowest_letter": "D"},
        {"name": "Croatia", "id": "104688944", "lowest_letter": "D"}, {"name": "Cyprus", "id": "106774002", "lowest_letter": "C"}, {"name": "Denmark", "id": "104514075", "lowest_letter": "E"},
        {"name": "Estonia", "id": "102974008", "lowest_letter": "C"}, {"name": "Faroe Islands", "id": "104630756", "lowest_letter": "B"}, {"name": "Finland", "id": "100456013", "lowest_letter": "D"},
        {"name": "France", "id": "105015875", "lowest_letter": "F"}, {"name": "Germany", "id": "101282230", "lowest_letter": "F"}, {"name": "Greece", "id": "104677530", "lowest_letter": "D"},
        {"name": "Guernsey", "id": "104019891", "lowest_letter": "B"}, {"name": "Hungary", "id": "100288700", "lowest_letter": "D"}, {"name": "Iceland", "id": "105238872", "lowest_letter": "C"},
        {"name": "Ireland", "id": "104738515", "lowest_letter": "D"}, {"name": "Isle of Man", "id": "106316481", "lowest_letter": "B"}, {"name": "Italy", "id": "103350119", "lowest_letter": "F"},
        {"name": "Jersey", "id": "102705533", "lowest_letter": "B"}, {"name": "Kosovo", "id": "104640522", "lowest_letter": "B"}, {"name": "Latvia", "id": "104341318", "lowest_letter": "C"},
        {"name": "Liechtenstein", "id": "100878084", "lowest_letter": "B"}, {"name": "Lithuania", "id": "101464403", "lowest_letter": "D"},
        {"name": "Luxembourg", "id": "104042105", "lowest_letter": "C"},
        {"name": "Malta", "id": "100961908", "lowest_letter": "C"}, {"name": "Moldova", "id": "106178099", "lowest_letter": "C"}, {"name": "Monaco", "id": "101352147", "lowest_letter": "B"},
        {"name": "Montenegro", "id": "100733275", "lowest_letter": "B"}, {"name": "Netherlands", "id": "102890719", "lowest_letter": "F"}, {"name": "Norway", "id": "103819153", "lowest_letter": "E"},
        {"name": "Poland", "id": "105072130", "lowest_letter": "E"}, {"name": "Portugal", "id": "100364837", "lowest_letter": "E"}, {"name": "Romania", "id": "106670623", "lowest_letter": "D"},
        {"name": "San Marino", "id": "105730022", "lowest_letter": "B"}, {"name": "Serbia", "id": "101855366", "lowest_letter": "D"}, {"name": "Slovenia", "id": "106137034", "lowest_letter": "C"},
        {"name": "Spain", "id": "105646813", "lowest_letter": "F"}, {"name": "Sweden", "id": "105117694", "lowest_letter": "E"}, {"name": "Switzerland", "id": "106693272", "lowest_letter": "E"},
        {"name": "Ukraine", "id": "102264497", "lowest_letter": "D"}, {"name": "United Kingdom", "id": "101165590", "lowest_letter": "G"},
        {"name": "Vatican City", "id": "107163060", "lowest_letter": "B"},
        {"name": "\u00c5land Islands", "id": "106452055", "lowest_letter": "B"}]

for el in data:
    add_biggest_companies(el["id"], el["name"], el["lowest_letter"], project)
