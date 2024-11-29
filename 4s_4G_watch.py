import socket


# 设置服务器的IP地址和端口
HOST = '127.0.0.1'  # 本地地址
PORT = 7998          # 监听的端口

# 创建一个 TCP/IP 套接字
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # 绑定套接字到地址
    server_socket.bind((HOST, PORT))
    while True:
        # 接收数据:
        data, addr = server_socket.recvfrom(1024) # 最大字节数
        dataStr = data.decode("utf-8")
        print("数据:",dataStr)

