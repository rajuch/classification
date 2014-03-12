"""Prepares input data for Gausian Bayesian classifier and categorize
the package into distributed and non-distributed..

@created: 10 Mar, 2014

@author: Raju Chinthala, <raju.chinthala@imaginea.com>
"""

# pylint: disable=W0105
# pylint: disable=W0141
# pylint: disable=W0401
# pylint: disable=W0602
# pylint: disable=W0614
# pylint: disable=W0621

import math
import MySQLdb as mdb
import numpy as np
from scipy.sparse import *
from sklearn.naive_bayes import GaussianNB
from time import time


def getDBConnection():
    user = "root"
    password = "root"
    databaseName = "cluster"
    conn = mdb.connect('localhost', user, password, databaseName)
    return conn


def executeSQL(con, sql):
    cursor = con.cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def get_packages():
    """Retrieve the package ID and distributed flag from the database.

    @return: Package IDs list and list of corresponding values for distributed
    flags of those packages.
    """
    sql = 'select id, distributed_flag from document order by id ASC'
    con = getDBConnection()
    rows = executeSQL(con, sql)
    pkgs = []
    distributed_flags = []
    for row in rows:
        pkgs.append(row[0])
        distributed_flags.append(row[1])
    return pkgs, distributed_flags


def get_clean_kwds():
    """Retrieve the key words, df value from the database."""
    con = getDBConnection()
    sql = "select word, df from clean_keywords"
    print sql
    clean_word_rows = executeSQL(con, sql)
    counter = 0
    word_df = {}
    for row in clean_word_rows:
        word, df = row
        word_df[word] = str(counter) + ":" + str(df)
        counter += 1
    return word_df


def prepare_data(pkgs):
    """Prepares the sparse matrix for Gausian Bayes classifier.

    @param pkgs: List of package IDs.
    """
    con = getDBConnection()
    row_count = 0
    max_tf_idf = 0
    for pkg_id in pkgs:
        sql2 = 'select name, tf from keywords where doc_id= ' + str(pkg_id)
        res = executeSQL(con, sql2)
        for row in res:
            word, tf = row
            if word in word_df:
                val = word_df[word]
                index, df = map(int, val.split(":"))
                tf_idf = tf * math.log(float(pkgs_count / df))

                x_coord[row_count, index] = tf_idf
                if max_tf_idf < tf_idf:
                    max_tf_idf = tf_idf
        row_count += 1


if __name__ == '__main__':
    t2 = time()
    pkgs, distributed_flags = get_packages()
    y_coord = np.array(distributed_flags)
    print 'shape of y_coord', y_coord.shape
    word_df = get_clean_kwds()

    pkgs_count = len(pkgs)
    kwds_count = len(word_df)
    # @todo(Logging info level)
    print pkgs_count, kwds_count
    #initialize the sparse matrix with the size of repositories and keywords
    x_coord = dok_matrix((pkgs_count, kwds_count), dtype=np.float32)
    print 'time taken for preparing data::' + str(time() - t2)
    prepare_data(pkgs)
    t3 = time()
    print 'time taken for preparing data::' + str(t3 - t2)
    t0 = time()

    clf = GaussianNB()
    clf.fit(x_coord.toarray()[0:100], y_coord[0:100])
    GaussianNB()
    res = clf.predict(x_coord.toarray()[100:])
    print 'actual values', y_coord[100:]
    print 'predicted values', res
