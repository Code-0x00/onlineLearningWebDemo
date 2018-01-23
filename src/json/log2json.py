import os
import string
def log2json(name):
    mb=r"""
,{"accuracy":%s,"iteration":"%s","l":0,"u":0}""" 
    os.system("cat {}.log |grep Test |grep Acc >{}.tmp".format(name,name))
    f=open("{}.tmp".format(name),'r')
    fj=open("{}.json".format(name),'w')
    fj.write(r"""[{"accuracy":0.0,"iteration":"0","l":0,"u":0}""" )
    count=0
    for line in f.readlines():
        count+=1
        acc=line.split('=')[-1].strip()
        fj.write(mb%(acc,str(count)))
    fj.write(']')
    fj.close()
    f.close()
if __name__=='__main__':
    log2json('xhq')
