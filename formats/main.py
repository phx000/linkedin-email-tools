import strategies
import utils


def main():
    project = utils.dict_query("select * from projects where name='HR'")[0]
    while True:
        result = strategies.simple_search(project)
        if result is None:
            return


main()
