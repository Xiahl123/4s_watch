import socket
import struct

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
        print(f"接收到数据: {data.decode('utf-8')}")
        # client_socket.sendall(data)  # 回送相同的数据

    client_socket.close()  # 关闭连接
    print(f"与 {addr} 的连接已关闭")
def parse_packet(hex_data):
    # 将十六进制字符串转换为字节
    packet = bytes.fromhex(hex_data)
    
    # 检查数据包长度
    if len(packet) < 6:
        raise ValueError("数据包长度不足")

    # 解析头部
    header = packet[:4]
    message_id = packet[4]
    payload_length = len(packet) - 6  # 6 = header + message_id + checksum
    
    # 解析有效负载
    payload = packet[5:-1]  # 取有效负载
    checksum = packet[-1]    # 最后一个字节是校验和

    # 解析不同的消息类型
    if message_id == 0xF0:  # 连接请求
        imei = struct.unpack('<Q', payload[:8])[0]  # 小端解析U64
        version = struct.unpack('<H', payload[8:10])[0]  # 小端解析U16
        return {
            'header': header,
            'message_id': message_id,
            'imei': imei,
            'version': version,
            'checksum': checksum
        }
    
    elif message_id == 0xF1:  # 连接回复
        token = struct.unpack('<I', payload[:4])[0]  # 小端解析U32
        return {
            'header': header,
            'message_id': message_id,
            'token': token,
            'checksum': checksum
        }
    
    elif message_id == 0xF9:  # 心跳包
        bat_type = payload[0]  # U8
        bat_volt = struct.unpack('<H', payload[1:3])[0]  # 小端解析U16
        signal_type = payload[3]  # U8
        signal_strength = struct.unpack('<H', payload[4:6])[0]  # 小端解析I16
        other_type = payload[6]  # U8
        num = struct.unpack('<I', payload[7:11])[0]  # 小端解析U32
        timestamp = struct.unpack('<I', payload[11:15])[0]  # 小端解析U32

        return {
            'header': header,
            'message_id': message_id,
            'bat_type': bat_type,
            'bat_volt': bat_volt,
            'signal_type': signal_type,
            'signal_strength': signal_strength,
            'other_type': other_type,
            'num': num,
            'timestamp': timestamp,
            'checksum': checksum
        }
    
    elif message_id == 0x02:  # 报警数据上传
        upl_warn = struct.unpack('<H', payload[:2])[0]  # 小端解析U16
        timestamp = struct.unpack('<I', payload[2:6])[0]  # 小端解析U32

        return {
            'header': header,
            'message_id': message_id,
            'upl_warn': upl_warn,
            'timestamp': timestamp,
            'checksum': checksum
        }
    
    elif message_id == 0x21:  # 报警数据上传补充
        alarm_type = struct.unpack('<H', payload[:2])[0]  # U16
        upl_warn = struct.unpack('<H', payload[2:4])[0]  # U16
        timestamp = struct.unpack('<I', payload[4:8])[0]  # U32

        return {
            'header': header,
            'message_id': message_id,
            'alarm_type': alarm_type,
            'upl_warn': upl_warn,
            'timestamp': timestamp,
            'checksum': checksum
        }

    else:
        raise ValueError("未知的消息ID")

import struct

def parse_downlink_packet(hex_data):
    # 将十六进制字符串转换为字节
    packet = bytes.fromhex(hex_data)
    
    # 检查数据包长度
    if len(packet) < 6:
        raise ValueError("数据包长度不足")

    # 解析头部
    header = packet[:4]
    message_id = packet[4]
    payload_length = len(packet) - 6  # 6 = header + message_id + checksum
    
    # 解析有效负载
    payload = packet[5:-1]  # 取有效负载
    checksum = packet[-1]    # 最后一个字节是校验和

    # 解析不同的下发消息类型
    if message_id == 0x17:  # 设置定位上报频率
        frequency = struct.unpack('<B', payload[:1])[0]  # U8
        return {
            'header': header,
            'message_id': message_id,
            'frequency': frequency,
            'checksum': checksum
        }
    
    elif message_id == 0x28:  # 信息下发
        message_length = payload[0]  # 首字节为消息长度
        message_content = payload[1:1 + message_length]  # 消息内容
        return {
            'header': header,
            'message_id': message_id,
            'message_content': message_content.decode('utf-16'),  # 假设为UTF-16编码
            'checksum': checksum
        }
    
    elif message_id == 0xCE:  # 综合设置
        setting_type = payload[0]  # 设置类型
        setting_value = struct.unpack('<H', payload[1:3])[0]  # 小端解析U16
        return {
            'header': header,
            'message_id': message_id,
            'setting_type': setting_type,
            'setting_value': setting_value,
            'checksum': checksum
        }
    
    elif message_id == 0xC3:  # 域名设置
        domain_length = payload[0]  # 域名长度
        domain_name = payload[1:1 + domain_length].decode('utf-8')  # 解码域名
        return {
            'header': header,
            'message_id': message_id,
            'domain_name': domain_name,
            'checksum': checksum
        }
    
    elif message_id == 0xCC:  # 久坐停留报警触发时间
        trigger_time = struct.unpack('<B', payload[:1])[0]  # U8
        return {
            'header': header,
            'message_id': message_id,
            'trigger_time': trigger_time,
            'checksum': checksum
        }
    
    elif message_id == 0x77:  # 关机重启
        action_type = payload[0]  # 0 = 关机, 1 = 重启
        return {
            'header': header,
            'message_id': message_id,
            'action_type': action_type,
            'checksum': checksum
        }
    
    else:
        raise ValueError("未知的消息ID")



if __name__ == '__main__':
    connectTcp()
    # 测试解析函数
  # hex_data_samples = [
  #     "BDBDBDBDF09B51731BC61603000014",  # 连接请求示例
  #     "BDBDBDBDF1BDBDBDB",  # 连接回复示例
  #     "BDBDBDBDF90120034A0B00E7",  # 心跳包示例
  #     "BDBDBDBD02020007FD8860E7",  # 报警数据上传示例
  #     "BDBDBDBD21020007FD8860E7"   # 报警数据上传补充示例
  # ]
  # for hex_data in hex_data_samples:
  #   try:
  #       result = parse_packet(hex_data)
  #       print("解析结果:", result)
  #   except ValueError as e:
  #       print("解析错误:", e)

  # 测试解析函数
  # hex_data_samples = [
  #     "BDBDBDBD1701E7",           # 设置定位上报频率示例
  #     "BDBDBDBD2805E4B1C8C4D5E8", # 信息下发示例
  #     "BDBDBDBDCE0203E7",         # 综合设置示例
  #     "BDBDBDBDC30574656E7",      # 域名设置示例
  #     "BDBDBDBDCC0A07E7",         # 久坐停留报警触发时间示例
  #     "BDBDBDBD7701E7"            # 关机重启示例
  # ]

  # for hex_data in hex_data_samples:
  #     try:
  #         result = parse_downlink_packet(hex_data)
  #         print("解析结果:", result)
  #     except ValueError as e:
  #         print("解析错误:", e)