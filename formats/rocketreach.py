import requests
from bs4 import BeautifulSoup
import random


def get_rocketreach_id_from_account_name(name):
    url = "https://search.yahoo.com/search"
    params = dict(p="+".join(name.strip().lower().split()) + "+rocketreach")
    req = requests.get(url, params=params)

    if req.status_code == 500:
        return -2

    if req.status_code != 200:
        return -1

    soup = BeautifulSoup(req.content, "html.parser")
    anchors = soup.find_all("a", class_="d-ib fz-20 lh-26 td-hu tc va-bot mxw-100p")
    found_rr_ids = {}

    for a in anchors:
        url = a.attrs["href"]
        if url.startswith("https://rocketreach.co/"):
            comp_path = url.replace("https://rocketreach.co/", "")
            if "_" in comp_path:
                rr_id = comp_path.split("_")[-1]
                if len(rr_id) == 16:
                    if rr_id not in found_rr_ids:
                        found_rr_ids[rr_id] = 0
                    found_rr_ids[rr_id] += 1

    if not found_rr_ids:
        return -1

    max_key = max(found_rr_ids, key=found_rr_ids.get)
    return max_key


def get_rocketreach_format_from_rocketreach_id(id_):
    url = f"https://rocketreach.co/{random.randint(1000, 1500)}-email-format_{id_}"
    req = requests.get(url)

    if req.status_code == 429:
        return -2

    if req.status_code != 200:
        return -1

    try:
        soup = BeautifulSoup(req.content, "html.parser")
        table = soup.find_all(class_="table")[0]
        tbody = table.find("tbody")
        trow = tbody.find("tr")
        format_part, domain_part = [el.text.strip().lower() for el in trow.find_all("td")[:2]]

        replacement_matrix = [
            ["[first]", "1"],
            ["[last]", "2"],
            ["[first_initial]", "3"],
            ["[last_initial]", "4"],
        ]

        for rep in replacement_matrix:
            format_part = format_part.replace(rep[0], rep[1])

        domain_part = domain_part.split("@")[1]
        full_format = format_part + "@" + domain_part

        return full_format
    except:
        return -1
