def clean_account_search_result(result):
    out = []
    employee_count_range_dict = {
        "1-10 employees": 0,
        "11-50 employees": 1,
        "51-200 employees": 2,
        "201-500 employees": 3,
        "501-1,000 employees": 4,
        "1,001-5,000 employees": 5,
        "5,001-10,000 employees": 6,
        "10,001+ employees": 7
    }
    for element in result["elements"]:
        if "companyName" not in element or "entityUrn" not in element:
            continue
        clean = {
            "name": element["companyName"],
            "urn": element["entityUrn"].replace("urn:li:fs_salesCompany:", ""),
            "employee_count_range": employee_count_range_dict[element["employeeCountRange"]]
            if "employeeCountRange" in element and str(element["employeeCountRange"]) in employee_count_range_dict
            else None,
            "industry": element["industry"] if "industry" in element and str(element["industry"]) else None
        }
        out.append(clean)
    return out


def clean_lead_search_result(result):
    out = []
    for element in result["elements"]:
        clean = {"geo_region": None, "title": None, "account_urn": None, "started_position_on_month": None, "started_position_on_year": None}

        if "firstName" in element and str(element["firstName"]):
            clean["first_name"] = str(element["firstName"])
        else:
            continue

        if "lastName" in element and str(element["lastName"]):
            clean["last_name"] = str(element["lastName"])
        else:
            continue

        if "objectUrn" in element and str(element["objectUrn"]):
            clean["urn"] = str(element["objectUrn"]).replace("urn:li:member:", "")
        else:
            continue

        if "geoRegion" in element and str(element["geoRegion"]):
            clean["geo_region"] = str(element["geoRegion"])

        if "currentPositions" in element and element["currentPositions"]:
            position = element["currentPositions"][0]

            if "companyUrn" in position:
                clean["account_urn"] = str(position["companyUrn"]).replace("urn:li:fs_salesCompany:", "")

            if "title" in position and str(position["title"]):
                clean["title"] = str(position["title"])

            if "startedOn" in position and "month" in position["startedOn"] and "year" in position["startedOn"]:
                if "month" in position["startedOn"]:
                    if str(position["startedOn"]["month"]).isnumeric():
                        clean["started_position_on_month"] = int(position["startedOn"]["month"])

                if "year" in position["startedOn"]:
                    if str(position["startedOn"]["year"]).isnumeric():
                        clean["started_position_on_year"] = int(position["startedOn"]["year"])
        else:
            continue
        out.append(clean)
    return out
