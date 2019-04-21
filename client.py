#!/usr/bin/env python
# -*- coding: utf-8 -*-#
'''
@Name:         client.py
@Description:  
@Author:       yanghao
'''

import socket

class Connection():
    # 管理客户端与redis server tcp连接
    def __init__(self,host='localhost',port=6379):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def connect(self):
        self.client.connect((self.host,self.port))

    def send(self,data):
        self.client.send(data.encode('utf-8'))

    def recv(self):
        return self.client.recv(65536)

class Client():
    # 客户端类，实现redis resp协议
    def __init__(self,host='localhost',port=6379,password=None,db=None):
        self.connection = Connection(host,port)
        self.password = password
        self.db = db or 0
        self.connection.connect()

    def format_command(self,*args,**kwargs):
        cmds = []
        for arg in args:
            # print(args)
            cmds.append('$%d\r\n%s\r\n' % (len(str(arg)),arg))
        return '*%d\r\n%s' % (len(args),''.join(cmds))

    def execute_command(self,cmd,*args,**kwargs):
        command = self.format_command(cmd,*args,**kwargs)
        self.connection.send(command)
        return self.connection.recv()

    def set(self,key,value):
        res = self.execute_command('SET',key,value)
        return self.extract_result(res.decode('utf-8'))

    def get(self,key):
        res = self.execute_command('GET',key)
        return self.extract_result(res.decode('utf-8'))

    def lpush(self,key,*value):
        res = self.execute_command('LPUSH',key,*value)
        return self.extract_result(res.decode('utf-8'))


    def extract_result(self,result):
        if result:
            res = result.split('\r\n')
            if res[0].startswith('+') or res[0].startswith(':'):
                return res[0][1:]
            elif res[0].startswith('$'):
                return ''.join(res[1:])
            elif res[0].startswith('*'):
                return [val for i,val in enumerate(res[1:]) if i%2!=0]
            else:
                raise Exception('Invalid Response: protocol error')


if __name__ == '__main__':
    ip = '192.168.31.184'
    port = 6379
    client = Client(host=ip,port=port)

    val = client.set('test1','redis')
    print(val)
    val = client.get('test1')
    print(val)

    li = [1,2,3,4]
    val = client.lpush('testlist',*li)
    print(val)




