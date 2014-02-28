'''
Created on 26-Feb-2014

@author: raju
'''
import os
import sys
import re
import MySQLdb as mdb
from pprint import pprint

stopwords = ['__main__', 'desc', 'true', 'false', 'service', 'type', 'none', 'to', 
             'in', 'up', 'for', 'or', 'not', 'is', 'all', 'date', 'exit', 'and', 'about',
             'yes', 'but', 'from', 'dir', 'use', 'with', 'by', 'juju', 'charm', 'charms',
             'on', 'other', 'home', 'stdout', 'stderr', 'it', 'even', 'as', 'the', 'sudo',
             'of', 'start', 'stop', 'apt-get', 'and', 'with','__init__.py','{0}','{}', 'out',
             'has','changed', 'so', 'can', 'could', 'are', 'no', 'download', 'print', 'aptitude',
             'install', 'installed', 'installation', 'en', 'min', 'max', 'user', 'name', 'now',
             'unable', 'started', 'stopping', 'stopped', 'updating', 'updated', 'update',
             'charm-helper-sh']

shellProcessList = frozenset(['pip', 'apt-get', 'aptitude', 'easy_install', 'yum', 'apt_get'])
INSTALL = '{0}install{0}'.format(' ')
syspath = '/home/raju/Work/classification/data/'

def extractPackagesNames(cmd):
    out = [i.strip('\'"\n') for i in cmd.split(INSTALL)[1].split() if not i.startswith('-')]
    return out

def checkWord(word):
    chList =['\\', '|', '/', ':', ';', '%', '$']
    word = word.strip(":;%") 
    for ch in chList:
        if ch in word:
            return False
    if word.isdigit():
        return False
    return True

def processShell(f, docId):
    print 'in shell'
    lines = map(str.strip, f)
    inMatch = filter(lambda x: INSTALL in x, lines)
    reqd = filter(lambda x:set(x.split()).intersection(shellProcessList), inMatch)
    keywords = list()
    for cmd in reqd:
        try:
            keywords.extend(extractPackagesNames(cmd))
        except:
            continue
    processKeywordsList(keywords, docId)
    for line in lines:
        if (line.startswith('#') or 'juju-log' in line):
            continue
        keywords = re.findall("[\"\'].*?[\"\']", line)
        for word in keywords:
            word = word.strip("\"'").lower()
            processKeywordsList(word.split(), docId)
        
def processKeywordsList(keywords, docId):
    if keywords is None or len(keywords) == 0:
        return
    
    for word in keywords:
        word = word.strip(".:=-,\"'\n $_%{}()[]").lower()
        if (not isEmpty(word)) and not (word in stopwords) and checkWord(word):
            insertCMD(word, docId)
            
def isEmpty(word):
    word = word.strip()
    l = len(word)
    if l <= 1:
        return True
    if word =='' or word == 'null' or word =='\\n' or word == '__main__':
        return True
    return False

def procesPy(f, docId):
    print 'in python'
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
                    w = w.strip(".:=-,\"'\n %_{}^()[]")
                    if (not isEmpty(w)) and (w not in stopwords) and checkWord(word):
                        insertCMD(w, docId)


def insertCMD(w, docId):
    cursor = conn.cursor()
    global keywordsIndex
    try:
        sql = 'INSERT INTO keywords VALUES (' + str(keywordsIndex) + ',"' + w + '",' +str(docId) + ',0)'
        print sql
        cursor.execute(sql)
        conn.commit()
        keywordsIndex += 1
    except Exception as e:
        print e
    return 

def insertDoc(docName, docIndex):
    sql = "INSERT INTO document VALUES (" + str(docIndex) + ',"'+ docName +'", null)'
    print sql
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        print e   

def processFile(root, fileName, docIndex):
    filePath = root + '/' + fileName
    if not os.path.islink(filePath):
        try:
            f = open(filePath, 'r')
            for line in f:
                if 'python' in line:
                    print filePath
                    procesPy(f, docIndex)
                    if fileName not in stopwords:
                        insertCMD(fileName, docIndex)
                elif 'bash' in line or 'bin/sh' in line:
                    print filePath
                    processShell(f, docIndex)
                    if fileName not in stopwords:
                        insertCMD(fileName, docIndex)
                break
        except Exception as e:
            print e

def read(rootDir, dirName, docIndex):
    for root, _, files in os.walk(rootDir + dirName):
        if('git' in root or '/tests' in root):
            continue
        for fileName in files:
            filePath = root + '/'+fileName
            processFile(root, fileName, docIndex)
           

if __name__ == '__main__':
    try:
        keywordsIndex = 1
        docIndex = 1
        conn =mdb.connect(host="localhost", user="root", passwd="root", db="cluster1")
        for dir_entry in os.listdir(syspath):
            insertDoc(dir_entry, docIndex)
            print dir_entry
            read(syspath, dir_entry, docIndex)
            docIndex +=1
    except Exception as e:
        import traceback
        print 'Exception:-', traceback.format_exc()
    finally:
        if conn:
            conn.close()
    
    