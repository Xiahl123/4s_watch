# coding=utf-8 
import socket
import json

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定端口:
    s.bind(('192.168.1.100', 3824))
    while True:
        # 接收数据:
        data, addr = s.recvfrom(1024) # 最大字节数
        dataLen = 0
        if data[0] == 0x88:
            dataLen = data[2]-4 # -4是减去crc校验
            # print("length_data:",dataLen)
            dataStr = ''
            for i_data in data:
                dataStr += '{:02X} '.format(i_data)
            print("data:",dataStr)
            # print('dataall:',dataStr[6:24])
            # if dataStr[6:24] == '00A99392FA00000000':
            #     dataClass = dataStr[34:36]
            #     match dataClass:
            #         case '1C':
            #             print("warn")
            #         case '22':
            #             print("heart")
            #             label = coverBig(dataStr[36:44]) # 标签号
            #             print("label:",label)
            #             count = int(coverBig(dataStr[44:48]),16) # 复位计数
            #             print("count:",count)
            #             soltid = int(coverBig(dataStr[48:52]),16) # soltid
            #             print("soltid:",soltid)
            #             labelV = int(coverBig(dataStr[52:56]),16) # 标签版本
            #             print("labelV:",labelV)
            #             labelS = dataStr[56:58] # 标签状态
            #             print("labelS:",labelS)
            #             labelE = dataStr[58:60] # 标签电压
            #             print("labelE:",labelE)
            #         case '1D':
            #             print("GPS local")
            #         case '24':
            #             print("bluetooth local")
                        
            #         case '28':
            #             print("GPS+bluetooth local")    

def coverBig(fStr):
    strLen = len(fStr)
    if strLen%2 !=0:
        print("error")
        return
    else:
        bigStr = ''
        for i in range(strLen,0,-2):
            bigStr += fStr[i-2:i]
        return bigStr
if __name__ == '__main__':
    print("udp server ")
    main()