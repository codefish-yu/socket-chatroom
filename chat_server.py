'''
chat room服务端
'''

from socket import *
import os, sys


HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST, PORT)

#将多个函数都要使用该变量，做成全局变量
#存储用户{name:address}
user = {}

#处理用户登录
def do_login(s,name,addr):
    #如果用户名已存在
    if name in user or '管理员' in name:
        s.sendto('用户名已存在'.encode(),addr)
        return
    else:
        s.sendto(b'OK',addr)

    #遍历通知其他人，xxx登录
    msg = '\n欢迎%s加入群聊'%name #\n:换行打印
    for i in user:
        s.sendto(msg.encode(),user[i])
    #保存新用户在内存中
    user[name] = addr

#处理聊天
def do_chat(s,name,text):
    msg = '\n%s:%s'%(name,text)
    #遍历的方式发送给所有其他客户端
    for i in user:
        #排除掉自己
        if i != name:
            s.sendto(msg.encode(),user[i])

#处理退出
def do_quit(s, name):
    msg = '\n%s 退出群聊'%name
    for i in user:
        if i == name:
            s.sendto(b'EXIT',user[i])
        else:
            s.sendto(msg.encode(),user[i])
    del user[name]


# 循环获取客户端请求
def do_request(s):
    while True:
        data, addr = s.recvfrom(1024)
        #客户端传来的data格式：[L name]
        #切割取出信息,2表示只切到前两个' ',防止把后面的聊天内容切开
        tmp = data.decode().split(' ',2)
        #用户名
        name = tmp[1]
        #根据不同请求类型，执行不同事件
        #登录
        if tmp[0] == 'L':
            do_login(s,name,addr)
        #聊天
        elif tmp[0] == 'C':
            do_chat(s,name,tmp[2])
        #退出
        elif tmp[0] == 'Q':
            do_quit(s,tmp[1])





# 搭建网络:udp传输
def main():
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(ADDR)
    #创建进程，一个用于服务端主动发消息给所有用户(管理员身份),一个用于接收用户请求并处理
    pid = os.fork()
    if pid == 0:
        #管理员消息处理
        # 因为处理管理员消息的子进程进程不会保存用户信息，所以先通过socket将信息发送给父进程，让他去处理(本质是进程间通信)
        while True:
            msg = input('管理员消息：')
            msg = 'C 管理员' + msg
            s.sendto(msg.encode(),ADDR) #发给父进程
    #父进程处理用户请求，要注意保存用户是在父进程的内存中，子进程获取不到
    else:
        do_request(s)  # 循环接收客户端请求


if __name__ == '__main__':
    main()