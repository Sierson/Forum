from flask import g
import psycopg2
from psycopg2.extras import DictCursor

def connect_db():
    conn = psycopg2.connect('postgres://vvpkgmcdlanydl:34737b0f4f8057073b3decc1fdc80d1b53576eabea03ae4db7a3fd5356af946a@ec2-54-234-28-165.compute-1.amazonaws.com:5432/dbd4m1ilc6f2jf', cursor_factory=DictCursor)
    conn.autocommit = True
    sql = conn.cursor()
    return conn, sql

def get_db():
    db = connect_db()

    if not hasattr(g, 'postgres_db_conn'):
        g.postgres_db_conn = db[0]

    if not hasattr(g, 'postgres_db_curr'):
        g.postgres_db_cur = db[1]

    return g.postgres_db_cur

def init_db():
    db = connect_db()

    db[1].execute(open('schema.sql', 'r').read())
    db[1].close()
    db[0].close()