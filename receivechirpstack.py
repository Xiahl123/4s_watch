# import socket
# import base64
# import json
# import datetime

# def main():
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     # 绑定端口:
#     s.bind(('192.168.9.101', 8090))
#     while True:
#         # 接收数据:
#         data, addr = s.recvfrom(1024) # 最大字节数
#         dataStr = data.decode("utf-8")
#         data64 = base64.b64decode(dataStr)
#         print("data:",dataStr)

# if __name__ == '__main__':
#     print("udp server ")
#     main()

import paho.mqtt.client as mqtt

client=mqtt.Client()
client.connect("192.168.9.101",1883)

def on_message(client,userdata,message):
  print(message.topic,message.payload)
client.subscribe("topic")
client.om_message=on_message

client.loop_forever()