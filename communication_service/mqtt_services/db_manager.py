#!/usr/bin/python

import os
import psycopg2
# import pymysql


class DBmanager(object):
    def __init__(self):
        self.pg_db = os.environ.get("POSTGRES_DB")
        self.pg_user = os.environ.get("POSTGRES_USER")
        self.pg_password = os.environ.get("POSTGRES_PASSWORD")
        self.pg_host = os.environ.get("POSTGRES_HOST")
        self.pg_port = int(os.environ.get("POSTGRES_PORT"))

    def create_table(self, tablename):
        cur = self.connection.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS {0}(\
                     time        TIMESTAMPTZ       NOT NULL,\
                     mac_addr    TEXT              NOT NULL,\
                     data        int           NULL);".format(tablename))

        cur.close()
        self.connection.commit()

    def hyperize_table(self, tablename):
        cur = self.connection.cursor()
        cur.execute("SELECT create_hypertable(%(table_name)s, 'time');", {"table_name": tablename})
        cur.close()
        self.connection.commit()

    def feed(self, tablename, mac, data):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO {0}(time, mac_addr, data)\
                     VALUES (NOW(), '{1}', {2});".format(tablename, mac, data))
        cur.close()
        self.connection.commit()

    def feed_or_create(self, tablename, mac, data):
        cur = self.connection.cursor()
        try:
            self.feed(tablename, mac, data)
        except psycopg2.errors.lookup("42P01"):
            self.connection.rollback()
            self.create_table(tablename)
            self.hyperize_table(tablename)
            self.feed(tablename, mac, data)
        cur.close()

    def doQuery(self, tablename):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM {0};".format(tablename))
        print(cur.fetchall())
        cur.close()

    def connect(self):
        self.connection = psycopg2.connect(host=self.pg_host,
                                           user=self.pg_user,
                                           password=self.pg_password,
                                           dbname=self.pg_db)

    def disconnect(self):
        if(self.connection):
            self.connection.close()
            print("PostgreSQL connection is closed")
