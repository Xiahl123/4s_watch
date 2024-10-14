import socket
import json
import datetime

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定端口:
    s.bind(('192.168.1.100', 3845))
    while True:
        # 接收数据:
        data, addr = s.recvfrom(1024) # 最大字节数
        dataStr = data.decode("utf-8")
        dataJson = json.loads(dataStr)
        print("数据:",dataStr)

if __name__ == '__main__':
    print("udp server ")
    main()
