import socket
import struct
import time

# 设置服务器的IP地址和端口
HOST = '0.0.0.0'  # 本地地址
PORT = 7998          # 监听的端口

def connectTcp():
# 创建一个 TCP/IP 套接字
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # 绑定套接字到地址
  server_socket.bind((HOST, PORT))
  # 开始监听连接，参数是最大连接数
  server_socket.listen(5)
  print(f"TCP服务器正在运行，监听 {HOST}:{PORT}...")
  while True:
    # 接受连接
    client_socket, addr = server_socket.accept()
    print(f"接收到来自 {addr} 的连接")
    
    # 处理客户端请求
    while True:
        data = client_socket.recv(1024)  # 接收数据
        if not data:
            break  # 如果没有数据，退出循环
        print(f"接收到数据: {data}")
        isConnect = parse_packet(data)  # 回送相同的数据
        if isConnect:
            # 获取当前时间戳（秒）
            current_timestamp = time.time()
            # 如果需要转换为整数（取整）
            timestamp = int(current_timestamp)
            timestamp_bytes = struct.pack('<I', timestamp)  # 小端格式
            message = timestamp_bytes + bytes.fromhex("F1BDBDBDBD")  # 示例消息
            sum = calculate_checksum(message)
            client_socket.sendall(message+sum)
    client_socket.close()  # 关闭连接
    print(f"与 {addr} 的连接已关闭")

# 解析数据包协议
def parse_packet(hex_data):
    packet = hex_data
    # 检查数据包长度
    if len(packet) < 6:
        raise ValueError("数据包长度不足")

    # 解析头部
    header = packet[:4]
    if header == 0xBDBDBDBD:
      message_id = packet[4]
      payload_length = len(packet) - 6  # 6 = header + message_id + checksum
      
      # 解析有效负载
      payload = packet[5:-1]  # 取有效负载
      checksum = packet[-1]    # 最后一个字节是校验和

      # 解析不同的消息类型
      if message_id == 0xF0:  # 连接请求
          imei = struct.unpack('<Q', payload[:8])[0]  # 小端解析U64
          version = struct.unpack('<H', payload[8:10])[0]  # 小端解析U16
          print('连接请求--imei:',imei,'version:',version,'checksum：',checksum)
          return True
      
      elif message_id == 0xF9:  # 心跳包
          powerType = payload[0]  # U8
          power = struct.unpack('<H', payload[1:3])[0]  # 小端解析U16
          signal_type = payload[3]  # U8
          signal_strength = struct.unpack('<H', payload[4:6])[0]  # 小端解析I16
          other_type = payload[6]  # U8
          num = struct.unpack('<I', payload[7:11])[0]  # 小端解析U32
          timestamp = struct.unpack('<I', payload[11:15])[0]  # 小端解析U32

          print("心跳包--电量：",power,"--信号强度：",signal_strength,"--扩展：",num,"--时间戳：",timestamp)
          return False
      
      elif message_id == 0x02:  # 报警数据上传
          upl_warn = struct.unpack('<H', payload[:2])[0]  # 小端解析U16
          # timestamp = struct.unpack('<I', payload[2:6])[0]  # 小端解析U32,补传

          print("报警信号：",upl_warn)
def calculate_checksum(buffer):
    ck_sum = 0
    N = len(buffer)  # 获取缓冲区的长度

    for i in range(N):
        ck_sum += buffer[i]
        ck_sum = ck_sum % 0x100  # 取模操作

    ck_sum = 0xFF - ck_sum  # 计算最终的校验和
    return ck_sum



if __name__ == '__main__':
    connectTcp()