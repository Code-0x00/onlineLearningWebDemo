import json
import os
def test():
	f=open('j.txt','w')
	t={'a':1,'b':3}
	data=[{'a':1,'b':2}]
	data.append(t)
	j=json.dumps(data)
	f.write(j)
	f.close()
	print j
if __name__=='__main__':
    test()
