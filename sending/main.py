import strategies
import utils


def main():
    project = utils.dict_query("select * from projects where name='HR'")[0]

    # database=utils.get_database_name_from_project_id(project["id"])
    # utils.query("update campaigns set status=false where id=1",commit=True,database=database)
    # utils.query("update messages set sent=false where id=1", commit=True, database=database)

    strategies.simple_strategy(project)


main()
