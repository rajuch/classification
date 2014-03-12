"""Retrieves the keywords from the repository script files and inserts into the
database.


@created: 26 Feb, 2014

@author: Raju Chinthala, <raju.chinthala@imaginea.com>
"""

# pylint: disable=W0141
# pylint: disable=W0603
# pylint: disable=W0621
# pylint: disable=W0702
# pylint: disable=W0703

import os
import re
import traceback

import src.preprocess.util as util
import src.constants as constants


def has_special_chars(word):
    """Checks if special characters are present in the word.

    @param word: Keyword.
    @return: Boolean value.
    """
    for ch in constants.SPECIAL_CHARS:
        if ch in word:
            return True
    if not any(c.isalpha() for c in word):
        return True
    return False


def extract_shell_kwds(fp, pkg_id):
    """Populate keywords from shell scripts into the database.

    @param fp: File pointer of the script file.
    @param pkg_id: ID value of the package in the database.
    """
    lines = map(lambda x: x.strip(' \n'), fp)
    eol_flag = False
    kwds = list()
    for line in lines:
        if line.startswith('#') or (not constants.INSTALL in line
                                    and not eol_flag):
            continue
        try:
            if eol_flag:
                # Collect continuation line package names.
                _kwds = line.split()
            else:
                _kwds = line.split(constants.INSTALL)[1].split()
            kwds.extend([i.strip('\'"\n\\')
                         for i in _kwds if not i.startswith('-')])
        except:
            continue
        if line.endswith('\\'):
            eol_flag = True
        else:
            eol_flag = False
    populate_keywords(kwds, pkg_id)


def populate_keywords(kwds, pkg_id):
    """Populate keywords into the keywords table of the database.

    @param kwds: List of keywords in any line in a package script file.
    @param pkg_id: ID value of the package in the database.
    """
    if not kwds:
        return
    for word in kwds:
        # @todo(Check data and use the special character-list
        #  variable in the constants' file.)
        word = word.strip(".:;=-,\"'\n $_%{}()[]^*?& +#`").lower()
        if len(word) <= 1 or (word in constants.STOP_WORDS) or \
        has_special_chars(word):
            continue
        insert_keyword(word, pkg_id)


def extract_python_kwds(fp, pkg_id):
    """Populate keywords from python script into the database.

    @param fp: File pointer of the script file.
    @param pkg_id: ID value of the package in the database.
    """
    for line in fp:
        line = line.strip(' \n').lower()
        if (line.startswith('#') or line.startswith("\'\'\'") or
                line.startswith("\"\"\"") or 'log(' in line):
            continue

        kwds_cluster = re.findall("[\"\'].*?[\"\']", line)
        if not len(kwds_cluster):
            continue

        for kwds in kwds_cluster:
            kwds = kwds.strip("\"'")
            populate_keywords(kwds.split(), pkg_id)


def insert_keyword(kwd, pkg_id):
    """Inserts the keyword into the table.

    @param kwd: keyword
    @param pkg_id: package id
    """
    global kwd_index
    try:
        sql = 'INSERT INTO keywords VALUES (' + str(kwd_index) + ',"' + kwd + '",' + str(pkg_id) + ',0)'
        print sql
        util.executeSQL(conn, sql)
        kwd_index += 1
    except Exception as e:
        print e
    return


def insert_package(pkg_name, pkg_id):
    """Inserts the package into the table.

    @param pkg_name: name of the package
    @param pkg_id:  Id of the package in database
    """
    sql = "INSERT INTO document VALUES (" + str(pkg_id) + ',"' + pkg_name + '", null, 0)'
    print sql
    try:
        util.executeSQL(conn, sql)
    except Exception as e:
        print e


def process_file(_dir, _name, pkg_id):
    """Populate keywords from python and shell scripts into the database.

    @param _dir: Directory path of the file.
    @param _name: File name.
    @param pkg_id: ID value of the package in the database.
    """
    file_path = os.path.join(_dir, _name)
    if os.path.islink(file_path):
        return
    try:
        fp = open(file_path, 'r')
        first_line = fp.readline()
        if constants.PYTHON in first_line:
            _func = extract_python_kwds
        elif constants.BASH in first_line or constants.SHELL in first_line:
            _func = extract_shell_kwds
        else:
            # Return if file is not a python or a shell script.
            return
        # Populates the keywords in the file.
        _func(fp, pkg_id)
        if _name not in constants.STOP_WORDS:
            insert_keyword(_name.split('.')[0], pkg_id)
    except Exception as e:
#         @todo(Logging, level info)
        print file_path, e


def populate_clean_keywords():
    """Populates the clean_keywords table."""
    try:
        print 'populate clean keywords table'
        sql = 'insert into clean_keywords(word, count) SELECT name,COUNT(*) as count FROM keywords GROUP BY name'
        print sql
        util.executeSQL(conn, sql)
    except Exception as e:
        print e


def delete_table_data():
    """Deletes the data from a table."""
    try:
        print 'delete existing data'
        sql = 'delete from document'
        sql1 = 'delete from clean_keywords'
        sql2 = 'delete from keywords'
        util.executeSQL(conn, sql)  # delete the existing data.
        util.executeSQL(conn, sql1)
        util.executeSQL(conn, sql2)
    except Exception as e:
        print e


def get_package_files(_dir):
    """Walks a directory path and gets file names in the tree.

    @param _dir: Path of the directory.
    @return: List of tuples of directory path and associated file name.
    """
    _files = []
    for root, _, files in os.walk(_dir):
        if('git' in root or '/tests' in root):
            continue
        for _name in files:
            _files.append((root, _name))
    return _files


def delete_keywords(pkg_id):
    """Deletes the keywords related to package from database

    @param pkg_id: Id of the package in database
    """
    sql = 'delete from keywords where doc_id = ' + str(pkg_id)
    util.executeSQL(conn, sql)
    return


def delete_package(pkg_id):
    """Deletes the package from database

    @param pkg_id: Id of the package in database
    """
    sql = 'delete from document where id = ' + str(pkg_id)
    util.executeSQL(conn, sql)
    return


def has_enough_keywords(pkg_id):
    """Checks whether the package has enough keywords to process.

    If the repository has only one keyword, then classifier would treat it
    as an origin and the result produced would be of no significance.

    @param pkg_id: Id of the package in database
    """
    sql = 'select count(*) from keywords where doc_id = ' + str(pkg_id)
    res = util.executeSQL(conn, sql)
    words_count = 0
    for row in res:
        words_count = int(row[0])
    if words_count < 2:
        delete_package(pkg_id)
        delete_keywords(pkg_id)
        return False
    return True


def calculate_TF_IDF():
    """Calculates the term frequency and inverse document frequency of
    the keywords and store them in the database tables.
    """
    conn = util.getDBConnection()
    sql = "select word from clean_keywords"
    print sql
    rows = util.executeSQL(conn, sql)
    word_tf = {}
    word_df = {}
    for row in rows:
        word = row[0]
        sql1 = "select doc_id from keywords where name='" + word + "'"
        print sql1
        res = util.executeSQL(conn, sql1)
        for row1 in res:
            pkg_id = row1[0]
            key = word + ':' + str(pkg_id)
            if key in word_tf:
                tf_count = word_tf[key]
                word_tf[key] = tf_count + 1
            else:
                word_tf[key] = 1
                if word in word_df:
                    df_count = word_df[word]
                    word_df[word] = df_count + 1
                else:
                    word_df[word] = 1

    for word, df in word_df.iteritems():
        sql = 'update clean_keywords set df=' + str(df) + " where word='" + word + "'"
        print sql
        util.executeSQL(conn, sql)

    for word_pkgid, tf in word_tf.iteritems():
        word, pkg_id = word_pkgid.split(":")
        sql = 'update keywords set tf=' + str(tf) + " where name='" + word + "' and doc_id=" + str(pkg_id)
        print sql
        util.executeSQL(conn, sql)


if __name__ == '__main__':
    try:
        kwd_index = 1
        pkg_id = 1
        conn = util.getDBConnection()
        delete_table_data()  # delete the existing data
        # @todo(Argparse)
        for _dir in os.listdir(constants.PATH):
            insert_package(_dir, pkg_id)
            # @todo(Logging)
            print _dir
            _files = get_package_files(os.path.join(constants.PATH, _dir))
            for root, _file in _files:
                process_file(root, _file, pkg_id)
 
            if has_enough_keywords(pkg_id):
                pkg_id += 1
        populate_clean_keywords()
        calculate_TF_IDF()
    except Exception as e:
        # @todo: Logs implementation.
        print 'Exception:-', traceback.format_exc()
