# binlog_parse_to_sql
binlog python解析
MySQL_Binlog_Parse_to_sql


======Author:GuiJiaoQi&XuYou                                              		
======For Example:python ts.py -u user -p password -f mysql-bin.00000x.sql -b binlog_to_sql.sql

Usage: ts.py [options]

      Options:
        -h, --help            show this help message and exit
        -u USER, --user=USER  User for login if not current user
        -p PASSWORD, --password=PASSWORD
                              Password to use when connecting
        -f FILE, --file=FILE  write binlog to file
        -b binlog, --report=binlog
                              incoming parse binlogfile For Example:mysqlbinlog
                              --no-defaults --base64-output=decode-rows -v -v mysql-
                              bin.00000x
