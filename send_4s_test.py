import socket

# 设置目标主机和端口
host = 'localhost'
port = 7998

# 创建 TCP 套接字
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    try:
        # 连接到目标主机
        client_socket.connect((host, port))
        
        # 发送消息
        message = '123456'
        client_socket.sendall(message.encode('utf-8'))
        
        print(f'已发送消息: {message}')
    except Exception as e:
        print(f'发生错误: {e}')