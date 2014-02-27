'''
Created on 26-Feb-2014

@author: raju
'''
import os
import sys
import keyword
import re
import MySQLdb as mdb
from pprint import pprint

stopwords = ['__main__', 'desc', 'true', 'false', 'service', 'type', 'none', 'to', 
             'in', 'up', 'for', 'or', 'not', 'is', 'all', 'date', 'exit']

shellProcessList = frozenset(['pip', 'apt-get', 'aptitude', 'easy_install', 'yum', 'apt_get'])
INSTALL = '{0}install{0}'.format(' ')
syspath = '/home/raju/Work/classification/data/'

def extractPackagesNames(cmd):
    out = [i.strip('\'"\n') for i in cmd.split(INSTALL)[1].split() if not i.startswith('-')]
    return out

def checkWord(word):
    chList =['\\', '|', '/', ':', ';', '%'] 
    for ch in chList:
        if ch in word:
            return False
    if word.isdigit():
        return False
    return True

def processShell(f, fileName, docId):
    print 'in shell'
    global index
    lines = map(str.strip, f)
    inMatch = filter(lambda x: INSTALL in x, lines)
    reqd = filter(lambda x:set(x.split()).intersection(shellProcessList), inMatch)
    keywords = list()
    for cmd in reqd:
        try:
            keywords.extend(extractPackagesNames(cmd))
        except:
            continue
    for word in keywords:
        if not isEmpty(word) and word not in stopwords and checkWord(word):
            insertCMD(word, index, docId)
            index += 1

def isEmpty(word):
    word = word.strip()
    l = len(word)
    if l <= 1:
        return True
    if word =='' or word == 'null' or word =='\\n' or word == '__main__':
        return True
    return False

def procesPy(f, fileName, docId):
    print 'in python'
    global index
    #keywordsFile = open('/home/raju/Work/classification/processed/' + fileName, 'w')
    for line in f:
        line = line.strip()
        if (line.startswith('#') or line.startswith("\'\'\'") or
            line.startswith("\"\"\"") or 'log(' in line):
            continue
        keywords = re.findall("[\"\'].*?[\"\']", line)
        if len(keywords) != 0:
            for word in keywords:
                word = word.strip("\"'").lower()
                for w in word.split():
                    w = w.strip(".:=-,\"'\n")
                    if not isEmpty(w) and w not in stopwords and checkWord(word):
                        insertCMD(w, index, docId)
                        index += 1


def insertCMD(w, index, docId):
    cursor = conn.cursor()
    try:
        sql = 'INSERT INTO keywords VALUES (' + str(index) + ',"' + w + '",' +str(docId) + ')'
        print sql
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        print e
    return 


def read(path):
    cursor = conn.cursor()
    i = 1
    for dir_entry in os.listdir(path):
        print dir_entry
        try:
            f = open(path + dir_entry + '/hooks/install', 'r')
            for line in f:
                if 'python' in line:
                    procesPy(f, dir_entry, i)
                else:
                    processShell(f, dir_entry, i)
                break
            sql = "INSERT INTO document VALUES (" + str(i) + ',"'+ dir_entry +'", null)'
            print sql
            i += 1
            try:
                cursor.execute(sql)
                conn.commit()
            except Exception as e:
                print e    
        except:
            pass
           

if __name__ == '__main__':
    try:
        index = 1
        conn =mdb.connect(host="localhost", user="root", passwd="root", db="cluster")
        read(syspath)
    except Exception as e:
        import traceback
        print 'Exception:-', traceback.format_exc()
    finally:
        if conn:
            conn.close()
    
    