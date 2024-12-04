import socket

def tcp_client(host, port):
    # 创建一个TCP套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # 连接到服务器
        client_socket.connect((host, port))
        print(f"已连接到 {host}:{port}")

        # 发送消息
        message = bytes.fromhex("bdbdbdbdf09b51731bc61603000014")  # 示例消息
        client_socket.sendall(message)
        print(f"发送消息: {message}")

        # 接收服务器的响应
        response = client_socket.recv(1024)  # 接收最多1024字节
        print(f"接收到响应: {response.decode('utf-8')}")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 关闭套接字
        client_socket.close()
        print("连接已关闭")

if __name__ == "__main__":
    server_host = '103.241.167.51'  # 服务器的IP地址
    server_port = 7998         # 服务器的端口
    tcp_client(server_host, server_port)