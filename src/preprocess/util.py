'''
Created on 28-Feb-2014

@author: raju
'''
import MySQLdb as mdb

def executeSQL(con,sql):
    cursor = con.cursor()
    cursor.execute(sql)    
    return cursor.fetchall()

def calculateTFIDF():
    """
    calculates the term frequency- inverse document frequency and stores in the table
    """
    cursor = conn.cursor()
    sql = "select word from clean_keywords"
    print sql
    rows = executeSQL(conn, sql)
    wordTFMap = {}
    wordDFMap = {}
    for row in rows:
        word=row[0]
        sql1 = "select doc_id from keywords where name='"+word+"'"
        print sql1
        res=executeSQL(conn, sql1)
        for row1 in res:
            repoId = row1[0]
            key = word + ':'+ str(repoId)
            if key in wordTFMap:
                tfCount = wordTFMap[key]
                wordTFMap[key] = tfCount+1
            else:
                wordTFMap[key] = 1
                if word in wordDFMap:
                    dfCount = wordDFMap[word]
                    wordDFMap[word] = dfCount+1
                else:
                    wordDFMap[word] =1
    
    for key in wordDFMap.keys():
        sql = 'update clean_keywords set df='+str(wordDFMap[key]) + " where word='"+key+"'"
        print sql
        cursor.execute(sql)
        conn.commit() 
        
    for key in wordTFMap.keys():
        row=key.split(":")
        sql = 'update keywords set tf='+str(wordTFMap[key])+" where name='"+row[0]+"' and doc_id="+str(row[1])
        print sql
        cursor.execute(sql)
        conn.commit()  

if __name__ == '__main__':
    conn =mdb.connect(host="localhost", user="root", passwd="root", db="cluster1")
    calculateTFIDF()