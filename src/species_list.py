#encoding:utf8
#!/usr/bin/python3

import sqlite3
class sq():
    def __init__(self,name):
        self.conn = sqlite3.connect('{}.db'.format(name))
        self.c = self.conn.cursor()
        try:
            self.table_create()
        except:
            print("Table already exist")

    def __del__(self):
        print 'close'
        self.conn.close()

    def table_create(self):
        print 'table'
        self.c.execute('''CREATE TABLE SPECIES (
            SP_NAME      TEXT PRIMARY KEY    NOT NULL,
            INS_DATE        TEXT 
            );''')
        self.conn.commit()

    def insert(self,spName,insDate):
        try:
            self.c.execute("""INSERT INTO SPECIES (SP_NAME,INS_DATE) \
                       VALUES ("%s",'%s')"""%(spName,insDate));
            self.conn.commit()
        except:
        	print "Item Already Insert.."

    def select(self):
            ret=[]
            cursor=self.c.execute("""SELECT SP_NAME,INS_DATE from SPECIES order by SP_NAME""")
            for row in cursor:
                tmp={}
                tmp['SP_NAME']=row[0].encode('unicode-escape').decode('string_escape')
                tmp['INS_DATE']=row[1].encode('unicode-escape').decode('string_escape')
                ret.append(tmp)
            return ret

    def delete(self,spName):
                c.execute("DELETE from SPECIES where SP_NAME='{}';".format(id))
                conn.commit()

if __name__=='__main__':
    s=sq('testss')
    s.insert("example","1122")
    print s.select()