import utils
import strategies


def main():
    project = utils.dict_query("select * from projects where name='HR'")[0]
    strategies.default_strategy(project)


main()
