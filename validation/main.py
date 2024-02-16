import strategies
import utils


def main():
    project = utils.dict_query("select * from projects where name='HR'")[0]
    strategies.simple_validation(project)


main()
