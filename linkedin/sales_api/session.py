import utils


class Session:
    def __init__(self):
        accounts = self.get_accounts_data()
        accounts_with_status = [{**account, "status": 200} for account in accounts]
        self.accounts = accounts_with_status

    def get_accounts_data(self):
        records = utils.dict_query("select name,data from sales_accounts")
        return records

    def get_account(self):
        for account in self.accounts:
            if account["status"] == 200:
                return account
        return None

    def flag_account(self, id_, flag):
        for account in self.accounts:
            if account["id"] == id_:
                account["status"] = flag
                return
