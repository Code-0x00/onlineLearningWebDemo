#encoding:utf8
#!/usr/bin/python3

import sqlite3
import os

class CrawlDB():
    def __init__(self,filename):
        if os.path.exists(filename):
            print("Opened database successfully ...")
            try:
                self.table_create()
            except:
                print('Waiting to insert ...')
        else:
            self.conn = sqlite3.connect('{}.db'.format(filename)) 
            self.c = self.conn.cursor()
            try:
                self.table_create()
            except:
                print('Warning:Failed to create table ...')

    def __del__(self):
        self.conn.close()
        print("Del CrawlDB ...")

    def table_create(self):
        self.c.execute('''CREATE TABLE CRAWL (
            URL      TEXT PRIMARY KEY    NOT NULL,
            KEYWORD        TEXT          NOT NULL
            );''')
        self.conn.commit()
        print ("Table created successfully");

    def insert(self,url,keyword):
        try:
            self.c.execute("""INSERT INTO CRAWL (URL,KEYWORD) VALUES ('%s','%s')"""%(url,keyword))
            self.conn.commit()
            return True
        except:
            self.c.execute("""UPDATE CRAWL set KEYWORD = '%s' where URL= '%s'"""%(keyword,url))
            self.conn.commit()
            return False

    def InsertList(self,list):
        count_insert=0
        for data in list:
            if self.insert(data['url'],data[keyword]):
                count_insert+=1
        return count_insert

    def select(self):
        count=0
        cursor=self.c.execute("""SELECT URL,KEYWORD from CRAWL""")
        for row in cursor:
            print("##%03d## "%count)
            count+=1
            print("URL = %s"%row[0])
            print("KEYWORD   = %s"%row[1])

    def delete(self,url):
        self.c.execute("DELETE from CRAWL where URL='%s';"%(url))
        self.conn.commit()

    def count(self):
        debug=self.c.execute("""select count(*) from CRAWL""")
        for i in debug:
            print(i[0])
            return i[0]

if __name__=='__main__':
    test=CrawlDB('test')
    test.count()