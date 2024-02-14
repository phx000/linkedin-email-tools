import requests
import utils


class Search:
    def __init__(self, type_, filters, keywords=None, start=0, count=100, spell_correction_enabled=False):
        if not filters and not keywords:
            raise Exception("'filters' and 'keywords' cannot be both empty")

        self.type_ = type_
        self.filters = filters
        self.keywords = keywords
        self.start = start
        self.count = count
        self.spell_correction_enabled = spell_correction_enabled

    def build_url(self):
        base_url = "https://www.linkedin.com/sales-api/salesApi{{search_type}}Search?q=searchQuery&query=({{query}})&start={{start}}&count={{count}}"
        filters_string = f"filters:List({','.join([str(fil) for fil in self.filters])})" if self.filters else None
        keywords_string = "keywords:" + " OR ".join([f'"{keyword}"' for keyword in self.keywords]) if self.keywords else None
        spell_correction_string = f"spellCorrectionEnabled:{'true' if self.spell_correction_enabled else 'false'}"
        query_string = ",".join([el for el in [spell_correction_string, filters_string, keywords_string] if el is not None])

        url = base_url.replace("{{search_type}}", "Lead" if self.type_ else "Account")
        url = url.replace("{{query}}", query_string)
        url = url.replace("{{start}}", str(self.start))
        url = url.replace("{{count}}", str(self.count))
        return url

    def search(self, headers):
        url = self.build_url()
        response = requests.get(url, headers=headers)
        return response.status_code, response.content
