import psycopg2
from psycopg2.extras import DictCursor
import traceback
import datetime
import json


def connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )


def query(query_, params=(), commit=False):
    conn = connection()
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


def dict_query(query_, params=()):
    conn = connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute(query_, params)
    data = cursor.fetchall()
    conn.close()
    return [dict(el) for el in data]


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
    current_comments = query(f"select comment from {table} where id=%s", (id_,))
    new_comment = {"datetime": str(datetime.datetime.now()), "comment": comment}
    current_comments.append(new_comment)
    query(f"update {table} set comment=%s where id=%s", (json.dumps(new_comment), id_,), commit=True)
