# -*- coding: utf-8 -*-
import sqlite3
import os
from datetime import datetime


def connect_db(db_file):
    return DBWrapper(db_file)

def add_record(db, table, andrew_id, nickname, metric):
    """
        Insert a new record if the andrew_id is not exist.
        Otherwise, update the existing record.
    """
    record = db.get_record_by_id(table, andrew_id)
    timenow = str(datetime.now())
    print record
    if not record:
        iter_list = []
        iter_list.append((andrew_id, nickname, metric, 1, timenow))
        db.instert_rows(table, record_schema, iter_list)
    else:
        updates = dict(
            andrew_id=andrew_id,
            nickname=nickname,
            metric=metric,
            submission=record[3]+1,
            time=timenow
        )
        db.update_record_by_id(table, andrew_id, updates)


record_schema = [
    ('andrew_id', 'TEXT PRIMARY KEY'),
    ('nickname', 'TEXT'),
    ('metric', 'DOUBLE'),
    ('submission', 'INTEGER'),
    ('time', 'TEXT')
]

class DBWrapper(object):
    """
        Wrapper class to store & retrieve dataset with sqlite3.
    """
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = None
        self.c = None

        self.dev_table = 'dev_tb'
        self.test_table = 'test_tb'

        self.connect()


    def connect(self):
        if self.connection is not None:
            self.connection.commit()
            self.connection.close()
        self.connection = sqlite3.connect(self.db_file)
        self.c = self.connection.cursor()

    def disconnect(self):
        if self.connection:
            self.connection.commit()
            self.connection.close()

    def _build_create_table_sql(self, tb_name, schema):
        col_names = ', '.join([c[0] + ' ' + c[1] for c in schema])
        return "CREATE TABLE IF NOT EXISTS {0} ({1})".format(tb_name, col_names)


    def ensure_tables(self):
        self.exe(self._build_create_table_sql(self.dev_table, record_schema))
        self.exe(self._build_create_table_sql(self.test_table, record_schema))


    def _build_insert_sql(self, tb_name, schema):
        question_marks = ', '.join(['?'] * len(schema))
        return "INSERT INTO {0} VALUES ({1})".format(tb_name, question_marks)


    def exe(self, sql, params=None):
        if params:
            return self.c.execute(sql, params)
        else:
            return self.c.execute(sql)


    def commit(self):
        self.connection.commit()
        self.c = self.connection.cursor()


    def instert_rows(self, tb_name, schema, iter_list):
        sql = self._build_insert_sql(tb_name, schema)
        for values in iter_list:
            self.c.execute(sql, tuple(values))
        self.commit()

    def get_all_records(self, table):
        sql = "SELECT * FROM {0}".format(table)
        return self.exe(sql)

    def get_record_by_id(self, table, andrew_id):
        sql = "SELECT * FROM {0} WHERE andrew_id = ?".format(table)
        self.exe(sql, (andrew_id,))
        return self.c.fetchone()
        

    def update_record_by_id(self, table, andrew_id, updates):
        sql = "UPDATE {0} SET nickname=?, metric=?, submission=?, time=? WHERE andrew_id=?".format(table)
        self.exe(sql, (updates['nickname'], updates['metric'], updates['submission'], updates['time'], updates['andrew_id']))
        self.commit()

    def create_index(self, tb_name, schema):
        sql = "CREATE INDEX {0}_idx ON {1} ({0})".format(col_name, tb_name)
        self.exe(sql)
        self.commit()


