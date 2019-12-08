'''
chat room 客户端
'''

from socket import *
import os,sys

#服务端地址,客户端ｙｉｉｄｎｇ会接收服务端地址
ADDR = ('127.0.0.1',8888)

#发消息的函数
def send_msg(s,name):
    while True:
        #捕获掉用户如果按ctrl+c的异常
        try:
            text = input('>>')
        except (KeyboardInterrupt,SyntaxError):
            text = 'quit'
        #退出的情况
        if text.strip() == 'quit':
            msg = 'Q' + name
            s.sendto(msg.encode(),ADDR)
            sys.exit('退出聊天室')   #进程退出，打印出:退出聊天室

        msg = 'C %s %s'%(name,text)
        s.sendto(msg.encode(),ADDR)

#接收消息
def recv_msg(s):
    while True:
        data,addr = s.recvfrom(4096)
        #发送消息的进程退出(表明用户要退出)，接收消息的进程也得跟着退出
        if data.decode() == 'EXIT':
            sys.exit()
        print(data.decode()+'\n>>',end='')  #\n>>表示换行打印出光标


#搭建网络
def main():
    s = socket(AF_INET,SOCK_DGRAM)

    #进入聊天室
    while True:
        name = input('请输入昵称：')
        msg = 'L ' + name   #通信协议与服务端确定好
        s.sendto(msg.encode(),ADDR)
        #接收反馈
        data,addr = s.recvfrom(128)
        # 登录成功，服务端会返回OK
        if data == b'OK':
            print('您已进入聊天室')
            break
        #登录失败，重新输入用户名
        else:
            print(data.decode())

    #已经进入聊天室,创建一个进程收消息，一个进程发消息，避免消息堵塞
    pid = os.fork()
    if pid < 0:
        sys.exit('Error!')
    elif pid == 0:
        send_msg(s,name)
    else:
        recv_msg(s)






if __name__ == '__main__':
    main()








