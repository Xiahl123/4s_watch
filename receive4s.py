import socket

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定端口:
    s.bind(('192.168.1.2', 8050))
    while True:
        # 接收数据:
        data, addr = s.recvfrom(1024) # 最大字节数
        print("receive:%s",data.decode("utf-8"))

if __name__ == '__main__':
    print("udp server ")
    main()
