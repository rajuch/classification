'''
Created on 26-Feb-2014

@author: raju
'''
import os
import sys
import re
import MySQLdb as mdb
from pprint import pprint

shellProcessList = frozenset(['pip', 'apt-get', 'aptitude', 'easy_install', 'yum', 'apt_get'])
INSTALL = '{0}install{0}'.format(' ')
syspath = '/home/raju/Work/classification/data/'

def extractPackagesNames(cmd):
    out = [i.strip('\'"\n') for i in cmd.split(INSTALL)[1].split() if not i.startswith('-')]
    return out

def processShell(f, outFile):
    print 'in shell'
    lines = map(str.strip, f)
    inMatch = filter(lambda x: INSTALL in x, lines)
    reqd = filter(lambda x:set(x.split()).intersection(shellProcessList), inMatch)
    #print reqd
    for cmd in reqd:
        outFile.write(cmd.strip(".:=-,\"'\n %_{}^()[]").lower())
        outFile.write('\n')

def isEmpty(word):
    word = word.strip()
    l = len(word)
    if l <= 1:
        return True
    if word =='' or word == 'null' or word =='\\n' or word == '__main__':
        return True
    return False

def procesPy(f, outFile):
    print 'in python'
    for line in f:
        line = line.strip()
        if (line.startswith('#') or line.startswith("\'\'\'") or
            line.startswith("\"\"\"") or 'log(' in line):
            continue
        keywords = re.findall("[\"\'].*?[\"\']", line)
        if len(keywords) != 0:
            l = ' '.join([x.strip("\"'") for x in keywords])
            if not isEmpty(l):
                outFile.write(l.strip(".:=-,\"'\n %_{}^()[]").lower())
                outFile.write('\n')
  

def processFile(root, fileName, outFile):
    filePath = root + '/' + fileName
    if not os.path.islink(filePath):
        try:
            f = open(filePath, 'r')
            for line in f:
                if 'python' in line:
                    print filePath
                    procesPy(f, outFile)
                elif 'bash' in line or 'bin/sh' in line:
                    print filePath
                    processShell(f, outFile)
                break
        except Exception as e:
            print e

def read(rootDir, dirName, outFile):
    for root, _, files in os.walk(rootDir + dirName):
        if('git' in root or '/tests' in root):
            continue
        for fileName in files:
            processFile(root, fileName, outFile)
           

if __name__ == '__main__':
    try:
        docIndex = 1
        conn =mdb.connect(host="localhost", user="root", passwd="root", db="cluster1")
        outputPath = '/home/raju/Work/classification/processed/'
        for dir_entry in os.listdir(syspath):
            print dir_entry
            outFile = open(outputPath + dir_entry, 'w')
            read(syspath, dir_entry, outFile)
    except Exception as e:
        import traceback
        print 'Exception:-', traceback.format_exc()
    finally:
        if conn:
            conn.close()
    
    