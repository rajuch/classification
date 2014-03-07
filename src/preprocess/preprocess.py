'''
Created on 26-Feb-2014

@author: raju
'''
import os
import sys
import re
import MySQLdb as mdb
from pprint import pprint
import src.preprocess.util as util

stopwords = ['__main__', 'desc', 'true', 'false', 'service', 'type', 'none', 'to', 
             'in', 'up', 'for', 'or', 'not', 'is', 'all', 'date', 'exit', 'and', 'about',
             'yes', 'but', 'from', 'dir', 'use', 'with', 'by', 'juju', 'charm', 'charms',
             'on', 'other', 'home', 'stdout', 'stderr', 'it', 'even', 'as', 'the', 'sudo',
             'of', 'start', 'stop', 'apt-get', 'with','__init__.py','{0}','{}', 'out',
             'has','changed', 'so', 'can', 'could', 'are', 'no', 'download', 'print', 'aptitude',
             'install', 'installed', 'installation', 'en', 'min', 'max', 'user', 'name', 'now',
             'unable', 'started', 'stopping', 'stopped', 'updating', 'updated', 'update',
             'charm-helper-sh', 'installing', 'cannot', 'data', 'are', 'foo', 'bar',
             'changes', 'changed', 'do', 'does', 'done', 'error', 'exists', 'exist', 'exiting',
             'fail', 'failed', 'failure', 'has', 'helper', 'id', 'include', 'into', 'list', 'min',
             'max', 'modules', 'name', 'must', 'new', 'on', 'pass', 'option', 'options', 'req',
             'required', 'self', 'sh', 'than', 'unable', 'update', 'updating', 'warning', 'where',
             'debug', 'info', 'critical', 'juju-log', 'add', 'already', 'charm-pre-install', 'charmhelpers',
             'check', 'status', 'running', 'run', 'joined', 'status', 'there', 'according', 'main',
             'parse', 'return', 'returned', 'generate', 'generating', 'dumping', 'dump', 'be', 'check',
             'checking', 'an', 'if', 'else', 'end', 'function', 'args', 'arg1', 'arg2', 'free', 'this',
             'come', 'alter', 'last', 'test', 'testing', 'argument']

shellProcessList = frozenset(['pip', 'apt-get', 'aptitude', 'easy_install', 'yum', 'apt_get'])
INSTALL = '{0}install{0}'.format(' ')
syspath = '/home/raju/Work/classification/data/'
pyFuncs = ['print', 'error', 'valueerror', 'juju-log']

def extractPackagesNames(cmd):
    out = [i.strip('\'"\n') for i in cmd.split(INSTALL)[1].split() if not i.startswith('-')]
    return out

def hasSpecialChars(word):
    chList =['\\', '|', '/', ':', ';', '%', '$', '=']
    word = word.strip(":;%") 
    for ch in chList:
        if ch in word:
            return True
    if not any(c.isalpha() for c in word):
        return True
    if word.isdigit():
        return True
    return False

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
        w = word.strip(".:;=-,\"'\n $_%{}()[]^ `").lower()
        if isEmpty(w) or (w in stopwords) or hasSpecialChars(word):
            continue
        insertCMD(w, docId)
            
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
        line = line.strip().lower()
        if (line.startswith('#') or line.startswith("\'\'\'") or
            line.startswith("\"\"\"") or 'log(' in line):
            continue
        funcFlag = False
        for func in pyFuncs:
            if line.startswith(func):
                funcFlag = True
                break
        if funcFlag:
            continue
        
        keywords = re.findall("[\"\'].*?[\"\']", line)
        if len(keywords) != 0:
            for word in keywords:
                word = word.strip("\"'").lower()
                for w in word.split():
                    w = w.strip(".:;=-,\"'\n%_{}^()[]$` ^")
                    if isEmpty(w) or (w in stopwords) or hasSpecialChars(word):
                        continue
                    insertCMD(w, docId)


def insertCMD(w, docId):
    global keywordsIndex
    try:
        sql = 'INSERT INTO keywords VALUES (' + str(keywordsIndex) + ',"' + w + '",' +str(docId) + ',0)'
        print sql
        util.executeSQL(conn, sql)
        keywordsIndex += 1
    except Exception as e:
        print e
    return 

def insertDoc(docName, docIndex):
    sql = "INSERT INTO document VALUES (" + str(docIndex) + ',"'+ docName +'", null)'
    print sql
    try:
        util.executeSQL(conn, sql)
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

def populateCleanKeywordsTable():
    try:
        print 'populate clean keywords table'
        sql = 'insert into clean_keywords(word, count) SELECT name,COUNT(*) as count FROM keywords GROUP BY name'
        print sql
        util.executeSQL(conn, sql)
    except Exception as e:
        print e

def deleteTableData():
    try:
        print 'delete existing data'
        sql = 'delete from document'
        sql1 = 'delete from clean_keywords'
        sql2 = 'delete from keywords'
        util.executeSQL(conn, sql) #delete the existing data
        util.executeSQL(conn, sql1)
        util.executeSQL(conn, sql2)
    except Exception as e:
        print e


def read(rootDir, dirName, docIndex):
    for root, _, files in os.walk(rootDir + dirName):
        if('git' in root or '/tests' in root):
            continue
        for fileName in files:
            processFile(root, fileName, docIndex)
           

if __name__ == '__main__':
    try:
        keywordsIndex = 1
        docIndex = 1
        conn = util.getDBConnection()
        deleteTableData() #delete the existing data
        for dir_entry in os.listdir(syspath):
            insertDoc(dir_entry, docIndex)
            print dir_entry
            read(syspath, dir_entry, docIndex)
            docIndex +=1
        populateCleanKeywordsTable()
        util.calculateTFIDF()
    except Exception as e:
        import traceback
        print 'Exception:-', traceback.format_exc()
   
    
    