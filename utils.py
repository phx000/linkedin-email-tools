import psycopg2
from psycopg2.extras import DictCursor
import traceback
import datetime
import json
import config


def connection(database):
    return psycopg2.connect(
        dbname=database.lower(),
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )


def query(query_, params=(), commit=False, database=config.APP_DATA_DB_NAME):
    conn = connection(database)
    cursor = conn.cursor()
    cursor.execute(query_, params)

    if commit:
        conn.commit()
        conn.close()
        return
    else:
        data = cursor.fetchall()
        conn.close()
        return data


def dict_query(query_, params=(), database=config.APP_DATA_DB_NAME):
    conn = connection(database)
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute(query_, params)
    data = cursor.fetchall()
    conn.close()
    return [dict(el) for el in data]


def dicts_commit(query_, dict_keys, dicts, database=config.APP_DATA_DB_NAME):
    conn = connection(database)
    cursor = conn.cursor(cursor_factory=DictCursor)
    for d in dicts:
        params = tuple(d[param] for param in dict_keys)
        cursor.execute(query_, params)
    conn.commit()
    conn.close()


def get_database_name_from_project_id(id_):
    return query("select name from projects where id=%s", (id_,))[0][0]


def stringify_exception(exception):
    info = [f"Exception type: {type(exception).__name__}",
            f"Exception message: {exception}",
            f"Exception arguments: {exception.args}",
            f"Cause: {exception.__cause__}",
            f"Context: {exception.__context__}",
            "Traceback:"]
    tb = traceback.format_tb(exception.__traceback__)
    info.extend(tb)
    return "\n".join(info)


def add_comment(comment, table, id_):
    current_comments = query(f"select comment from {table} where id=%s", (id_,))[0][0]
    if current_comments is None:
        current_comments = []
    new_comment = {"datetime": str(datetime.datetime.now()), "comment": comment}
    current_comments.append(new_comment)
    query(f"update {table} set comment=%s where id=%s", (json.dumps(current_comments), id_,), commit=True)


# todo update this function once Prometheus is finished
def create_project_database(project):
    # def create_accounts_table():
    #     cursor.execute(f"create table if not exists")

    # conn = connection(config.APP_DATA_DB_NAME)
    # conn.autocommit = True
    # cursor = conn.cursor()
    # cursor.execute(f"create database {project['name'].lower()}")
    # conn.close()

    conn = connection(project["name"].lower())
    cursor = conn.cursor()
    cursor.execute('''create table accounts(id serial primary key, name text not null check (name != ''), urn text not null unique check(urn != ''), employee_count_range int, industry text)''')

    conn.commit()
    conn.close()
