"""Database APIs.

@created: 28 Feb, 2014

@author: Raju Chinthala, <raju.chinthala@imaginea.com>
"""

import MySQLdb as mdb


def executeSQL(con, sql):
    cursor = con.cursor()
    cursor.execute(sql)
    con.commit()
    return cursor.fetchall()


def getDBConnection():
    user = "root"
    password = "root"
    databaseName = "cluster"
    conn = mdb.connect('localhost', user, password, databaseName)
    return conn
