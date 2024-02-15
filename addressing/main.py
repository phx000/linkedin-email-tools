import strategies
import utils


def main():
    project = utils.dict_query("select * from projects where name='HR'")[0]
    strategies.generate_addresses_from_all_leads(project)

main()
