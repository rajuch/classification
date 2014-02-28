'''
Created on 29-Jul-2013

@author: rajuc
'''
import numpy as np
from scipy.cluster.vq import vq, kmeans
from scipy.sparse import *
from scipy import *
from math import log
from sklearn import metrics
from sklearn.cluster import KMeans
from time import time
import MySQLdb as mdb

def getDBConnection():
    user = "root"
    password = "root"
    databaseName = "cluster"
    conn = mdb.connect('localhost', user, password, databaseName)
    return conn
    
def executeSQL(con,sql):
    cursor = con.cursor()
    cursor.execute(sql)    
    return cursor.fetchall()

def getRepos():
    """
    retrieve the repository ids, languages from the database
    """
    sql = 'select id from document order by id ASC'
    con = getDBConnection()
    rows= executeSQL(con, sql);
    repoList = []
    for row in rows:
        repoList.append(row[0])
    return repoList

def getCleanKeywords():
    """
    retrieve the words, document frequency>5 from the database
    """
    con = getDBConnection()
    sql = "select word, df from clean_keywords where df>1"
    print sql
    cleanWordRows = executeSQL(con, sql)
    counter =0
    wordDFMap ={}
    for row in cleanWordRows:
        word = row[0]
        df = row[1]
        wordDFMap[word] = str(counter)+":"+str(df)
        counter = counter+1
    return wordDFMap
   
def preapreData():
    """
    prepares the sparse matrix for kmeans
    """
    con = getDBConnection()
    rowCount =0
    global repoLangMap    
    for repoId in repoList:
        sql2 = 'select name, tf from keywords where doc_id= '+ str(repoId)
        #print sql2
        res = executeSQL(con, sql2)
        #print len(res), repoId
        for row in res:
            word = row[0]
            tf = int(row[1])
            if word in wordDFMap:
                val=wordDFMap[word]
                index = int(val.split(":")[0])
                df = int(val.split(":")[1])
                #print rowCount, index
                S[rowCount, index] = tf * math.log(float(noOfRepos/df))
           
        rowCount = rowCount + 1

def decodeClusterOutput(path,fileName):
    """
    decodes the cluster output(binary format) and writes to the new file
    input: fileName - cluster output file name
    """
    repoList=getRepos()
    a=np.fromfile(path+fileName,dtype=np.int64)
    count=0
    clusterMap ={}
    f = open(path+'clusteroutput_100','w')
    for key in a:
        if key in clusterMap:
            indexes= clusterMap[key] 
            clusterMap[key] = indexes + ":" + str(count) 
        else :
            clusterMap[key] = str(count)
        count +=1

    for key in clusterMap.keys():
        indexes = clusterMap[key]
        arr = indexes.split(":")
        string =''
        for val in arr:
            if string =='':
                string= str(repoList[int(val)])
            else:
                string= string + ","+str(repoList[int(val)])
        print string
        f.write(string)
        f.write('\n')
    f.close()


    
"""
variables declaration
"""

if __name__ == '__main__':
    t2 = time()        
    repoLangMap = {}
    langMap = {}
    repoList=getRepos()
    wordDFMap=getCleanKeywords()
    noOfWords=len(wordDFMap)
 
    noOfRepos = len(repoList)
    noOfKeyWords = len(wordDFMap)  
    print noOfRepos, noOfKeyWords
    #initialize the sparse matrix with the size of repositories and keywords
    S = dok_matrix((noOfRepos,noOfKeyWords), dtype = np.float32)
    print 'time taken for preparing data::' + str(time()-t2)
    preapreData() 
    t3 = time()
    print 'time taken for preparing data::' + str(t3-t2)
    t0 = time()

    path = '/home/raju/Work/classification/cluster/'
    clusterCentroidsFile = 'clusetCentroidsbin'
    clusterOutputFile = 'clusterutputbin'

    # computing K-Means with K = 100 (100 clusters)
    print 'shape of array', S.get_shape()
    centroids,_ = kmeans(S.toarray(),10, iter=50)
    np.ndarray.tofile(centroids,path+clusterCentroidsFile)
    print centroids

    # assign each sample to a cluster
    idx,_ = vq(S.toarray(),centroids)
    np.ndarray.tofile(idx,path+clusterOutputFile)
    print idx

    decodeClusterOutput(path,clusterOutputFile)
    t1 = time()
    print 'kmeans time::' + str(t1-t0)

