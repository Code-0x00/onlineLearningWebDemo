#!/usr/bin/env python
# encoding: utf-8

import requests
import re
import json
import os
import sys
import argparse
import threading
from time import sleep

#import xHeaders
import DBClass
#import xPlot

import multiprocessing


def error_print(error):
    f=open('error.log','a')
    
    str="""
    #####-error-start-#####
    %s
    #####-error-end-#####
    """%(error)
    f.write(str)
    f.close()
    
class Bing():
    def __init__(self,keyword=''):
        self.keyword=keyword
        self.count=0
        self.first=1
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
           'AppleWebKit/537.36 (KHTML, like Gecko) '
           'Chrome/56.0.2924.87 Safari/537.36',
           'Referer': 'https://cn.bing.com/images/'}
        self.url='http://cn.bing.com/images/async'
        self.params={
              'q': keyword,
              'first':'1',
              'count':'35',
              'relp':'35',
              'mmasync':'1',
              'lostate':'r',
              'mmasync':'1',
              'dgState':'x*0_y*0_h*0_c*3_i*36_r*9',
              'SFX':'2',
              'iid':'images.5756'
              }
        self.requestSession = requests.session()
        self.requestSession.get(url=self.url,
                                params=self.params,
                                headers=self.headers,
                                timeout=10)
        self.json_save=open(keyword+'.json','w')
        self.json_list=[]
        self.db=DBClass.CrawlDB(keyword)
        
        f=open('error.log','w')
        f.close()

    def html_save(self,filename='save.html'):
        f=open(filename,'wb')
        f.write(self.html.text.encode('utf-8'))
        f.close()
        
    def max_page_get(self):
        html = self.requestSession.get(self.url.format('1'))
        try:
            self.max_page=int(re.findall('javascript:goto_page\((.+?)\)',html.text,re.S)[-1])
        except:
            self.max_page=0
            self.html=html
            self.html_save()
        #self.html=html
        #self.html_save()
        print(self.max_page)
    def htmlget(self):
        self.html = self.requestSession.get(url=self.url,params=self.params,headers=self.headers,timeout=10)
        return self.html.text
        
    def read(self):
        mechstr="""<img class=\"mimg\"(.+?)/>"""
        ret=[]
        content=self.html.text
        server_text=re.findall(mechstr,content,re.S)
        for i in server_text:
            link=re.findall("src=\"(.+?)\"",content,re.S)
            for j in link:
                ret.append(j)
        return ret
        
    def get2db(self):
        self.max_page_get()
        if self.max_page==0:
            return -1
        else:
            for i in range(1,self.max_page+1):
                url=self.url.format(str(i))
                self.htmlget(url)
                list=self.read()
                for gold in list:
                    self.db.insert(gold['data_id'],gold['time'],gold['mhb'],gold['rmb'])
            #self.db.select()
    def crawler(self,keyword):
        count=0
        xlist=[]
        for i in range(10):
            print 'page',i
            self.first=i*35
            self.params['first']=str(self.first)
            self.htmlget()
            link=self.read()
            
            tmp_list=[]
            link.sort()
            turl=''
            for i in link:
            	if not i in tmp_list:
            		if 'http' in i:
            			tmp_list.append(i)
            xlist+=tmp_list
            new_count=len(xlist)
            print new_count
            if new_count==count:
                break
            else:
                count=new_count
        print len(xlist)
        xlist.sort()
        j=json.dumps(xlist)
        f=open(keyword+'.url','w')
        for i in xlist:
        	f.write(i+'\n')
        f.close()
        return len(xlist)

    def downloading(self,keyword):
        f=open(keyword+'.url','r')
        c=0
        for i in f.readlines():
        	name=keyword+"%04d.jpg"%c
        	c+=1
        	try:
        		rep=requests.get(i,headers=self.headers,stream=True)
        		rep.raise_for_status()
        		with open(name,'wb') as f:
        			for ck in rep:
        				f.write(ck)
        	except:
        		continue

def xCrawl(lock,keyword):
	    cbg=Bing(keyword)
	    xlen=cbg.crawler(keyword)
	    if lock.acquire():
	    	f=open('src/json/xhq.list.json','r')
	    	try:
	    		j=json.loads(f.read())
	    	except:
	    		j=[]
	    	flag=0
	    	for i in range(len(j)):
	    		if j[i]["n"]==keyword:
	    			j[i]["state"]="downloading %05d "%(xlen)
	    			flag=1
	    			break
	    	if flag==0:
	    		t={"n":"{}".format(keyword),"state":"downloading {}".format(str(xlen))}
	    		j.append(t)
	    	sj=json.dumps(j)
	    	f.close()

	    	f=open('src/json/xhq.list.json','w')
	    	f.write(sj)
	    	f.close()
	    	lock.release()



	    cbg.downloading(keyword)
	    if lock.acquire():
	    	f=open('src/json/xhq.list.json','r')
	    	j=json.loads(f.read())
	    	flag=0
	    	for i in range(len(j)):
	    		if j[i]["n"]==keyword:
	    			j[i]["state"]="downloaded %05d "%(xlen)
	    			flag=1
	    			break
	    	if flag==0:
	    		t={"n":"{}".format(keyword),"state":"downloaded {}".format(str(xlen))}
	    		j.append(t)
	    	sj=json.dumps(j)
	    	f.close()

	    	f=open('src/json/xhq.list.json','w')
	    	f.write(sj)
	    	f.close()
	    	lock.release()


if __name__ == '__main__':
    list=["airplane","automobile","bird","cat","deer","dog","frog","horse","ship","truck"]
    #for i in list:
    cbg=Bing(list[0])
    cbg.crawler()
