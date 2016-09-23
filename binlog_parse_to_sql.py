#!/usr/bin/python
# -*- coding:utf8 -*-



#######Comment:####################################################################
##	Author:GuiJiaoQi&XuYou	MAIL:yinyi1117@126.com;QQ:85531861		 ##
######	set global group_concat_max_len =1024000;避免group_concat  默认长度不够   ##
######	如果binlog文件的表在后面发生表结果变化，这个解析会报错			 ##
######  如果columns是二进制的解析会报错，如果有二进制的还请换工具，抱歉               ##
###################################################################################

import os,sys
import re
import MySQLdb

import optparse



def main():
        p = optparse.OptionParser()
	p.add_option('-u','--user',type='string',dest='user',default='root',
			help='User for login ')
	p.add_option('-p','--password',type='string',dest='password',
                        help='Password to use when connecting')
        p.add_option('-s','--socket',type='string',dest='socket',
                      help='The socket file to use for connection.')
        p.add_option('-f','--file',type="string",dest='filename',
                        help="incoming parse binlogfile For Example:mysqlbinlog  --no-defaults --base64-output=decode-rows -v -v mysql-bin.00000x",metavar='FILE')
        p.add_option('-b','--report',dest='binlog',help="write format binlog to normal sql",metavar='binlog')
        print "\n      ==========================================================================================\n======Author:GuiJiaoQi&XuYou                                              			=======\n======For Example:python ts.py -u user -p password -f mysql-bin.00000x.sql -b binlog_to_sql.sql =======\n      ==========================================================================================\n"
        (options, arguments) = p.parse_args() 
        out_in_binlog = options.filename 
	binlog_to_sql = options.binlog
	if str(out_in_binlog) == 'None'  :
		p.print_help() 
	
	return str(out_in_binlog)+','+str(binlog_to_sql)+','+str(options.user)+','+str(options.password)+','+str(options.socket)



main= main()


if main.split(',')[0] == 'None':
	exit();
else:
	user=main.split(',')[2]
	passwd=main.split(',')[3]
	socket=main.split(',')[4]

if socket == 'None':
        conn1=MySQLdb.connect(host="localhost",user=user,passwd=passwd,port=3306,db="information_schema",read_default_file="/etc/my.cnf",charset="utf8")
else:
        conn1=MySQLdb.connect(host="localhost",user=user,passwd=passwd,port=3306,db="information_schema",read_default_file="/etc/my.cnf",charset="utf8",unix_socket=socket)
        
cursor=conn1.cursor()

def get_columns(db_tb_name):
	try:
		db_name_1 = db_tb_name.split('|')[0]
                tb_name_1 = db_tb_name.split('|')[1]
		cursor.execute('select group_concat(column_name) cls from information_schema.COLUMNS where table_schema="%s" and table_name="%s"' %(db_name_1,tb_name_1))
		row1 = cursor.fetchall()
		cls = str(row1[0])
		cls = cls.decode('utf-8');
		#list_cls =  cls.replace('u','').replace('\'','').replace('(','').replace(',)','').split(',')
		list_cls = cls.replace("u'",'').replace('\'','').replace('(','').replace(',)','').split(',')
		len_li = len(list_cls)
		return list_cls
	except Exception as e:
        	print e



def _get_table_name(i):
       try:
                if i.find('Table_map:')!=-1:
                        l = i.index('Table_map')
                        tb_name = i[l::].split(' ')[1].replace('`','').split('.')[1]
                        db_name = i[l::].split(' ')[1].replace('`','').split('.')[0]
                        db_tb_name= db_name+'|'+tb_name
                        return  db_tb_name
       except Exception as e:
                print e


binlog_to_sql =  main.split(',')[1]
out_in_binlog = main.split(',')[0]

res = open(binlog_to_sql,'w')
fh = open(out_in_binlog,'r')



lines = ''

while True:
	i = fh.readline()

	if i == '':
		break

	i = i.decode('utf-8')
        
	current = ''

	if i.find('Table_map:') !=-1:  
		lineCls = _get_table_name(i)
		list_cls = get_columns(lineCls)
	if '###' in i:
		
		if i.find('###   @') !=-1:
			ix1 = i.replace('###   @','').split('=')[0]
			ixx1 =  i.replace('###   @'+str(ix1),list_cls[int(ix1)-1]), 
			ixx1 = ''.join(ixx1);   
			if (int(ix1) == len(list_cls)):
				#line =  re.sub('/.* */','',ixx1)
				line = re.sub('\(\d+\)',' ',ixx1)
				line =  re.sub('/\*.*/','',line)
				                             
	                        current += line.replace('\n','').replace("('",'').replace("\\n'",'').replace(',)','').replace('\\n"','').replace('("','').replace('(255)','').replace('(65535)','')
				lines += current
				
				if lines.find('INSERT') !=-1:           
                        		lineRe = re.search('INSERT (.*`) SET(.*)',lines)
                        		if not lineRe:
                                		#res.write(lines.encode('utf-8')+"\n")
                                		continue
                        		res.write("INSERT  "+lineRe.group(1).encode('utf-8')+" VALUES("+re.sub('\w+=','',lineRe.group(2).encode('utf-8'))+");\n")
                		elif lines.find('UPDATE') !=-1:
                        		lineRe = re.search('UPDATE (.*`) WHERE(.*) SET(.*)',lines)
                        		if not lineRe:
                                		#res.write(lines.encode('utf-8')+"\n")  
                                		continue
                        
                        		res.write("UPDATE "+lineRe.group(1).encode('utf-8')+" SET "+lineRe.group(3).encode('utf-8')+" WHERE "+lineRe.group(2).encode('utf-8').replace(',',' AND ')+";\n")
                		elif lines.find('DELETE') !=-1:
                        		lineRe = re.search('DELETE (.*`) WHERE(.*)',lines)
                        		if not lineRe:
                                		#res.write(lines.encode('utf-8')+"\n")  
                                		continue
                        		res.write("DELETE FROM  "+lineRe.group(1).encode('utf-8')+" WHERE "+lineRe.group(2).encode('utf-8').replace(',',' AND ')+";\n")
                		else:
                        		res.write(lines+"\n")
			else:
				#line = re.sub('/.* */',',',ixx1)  
				line = re.sub('\(\d+\)',' ',ixx1)
                                line = re.sub('/\*.*/',',',line)
			current += line.replace('\n','').replace("('",'').replace("\\n'",'').replace(',)','').replace('\\n"','').replace('("','').replace('(255)','').replace('(65535)','')
		else: 
			current += i.replace('### ','').replace('\n',' ')
	
	else:
		res.write(i)
		continue

	
	if current.find('INSERT') != -1 or current.find('UPDATE') != -1 or current.find('DELETE') != -1 :
		if not lines:
			lines += current
			continue
		lines = current 
		
	else:
		lines += current

fh.close()



