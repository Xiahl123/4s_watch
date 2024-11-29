# coding=utf-8 
import socket
import json
import time
import binascii

def main(fServer):
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # # 绑定端口:
    # s.bind(('192.168.1.100', 3824))
    while True:
        # 接收数据:
        data, addr = fServer.recvfrom(1024) # 最大字节数
        dataStr = ''
        for i_data in data:
                dataStr += '{:02X}'.format(i_data)
        print("data:",dataStr)
        mLen = len(data)
        mCrc16 = crc16_ccitt(data[0:mLen-2])
        print("crc16:",mCrc16)
        dataLen = int(dataStr[4:6],16)*2  # 这里乘2是计算字符数量
        dataGateway = '' #中继网关编号
        dataSendCount = 0 #中继发送数据的次数
        dataGatewayRestart = 0 #中继复位次数
        originIp = '' #源地址
        targetIp = '' #目标地址
        msgTime = ''
        msgReceive = ""
        if data[0] == 0x88:
            match data[1]:
                case 0x02: #仅包含源地址
                    originIp = coverBig(dataStr[8:16])
                    msgReceive = "源地址包"
                    decodeINS(dataStr[16:dataLen+8])
                case 0x04: #包含目标地址
                    targetIp = coverBig(dataStr[8:16])
                    msgReceive = "目标地址包"
                    decodeINS(dataStr[16:dataLen+8])
                case 0x20: #包含时间戳信息
                    mTime = hex2Int(dataStr[8:32])
                    msgReceive = "时间信息包"
                    #转换成localtime
                    time_local = time.localtime(mTime)
                    #转换成新的时间格式(2016-05-05 20:28:54)
                    msgTime = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
                    decodeINS(dataStr[32:dataLen+8])
                case 0x40: #包含中继设备信息（网关编号，网关重启次数，网关发送次数）
                    msgReceive = "设备信息包"
                    dataGateway = coverBig(dataStr[8:16])
                    dataGatewayRestart = hex2Int(dataStr[16:24])
                    dataSendCount = hex2Int(dataStr[24:32])
                    decodeINS(dataStr[32:dataLen+8])
                case 0x46: #ping上报协议，存在源地址+目标地址+中继负载信息
                    msgReceive = "ping包"
                    originIp = coverBig(dataStr[8:16])
                    targetIp = coverBig(dataStr[16:24])
                    dataGateway = coverBig(dataStr[24:32])
                    dataGatewayRestart = hex2Int(dataStr[32:40])
                    dataSendCount = hex2Int(dataStr[40:48])
        print("end-收到：",msgReceive,"-时间-",msgTime,"-源地址-",originIp,"-目标地址-",targetIp,"-网关编号-",dataGateway,"-网关重启数-",dataGatewayRestart,"-数据编号-",dataSendCount)
              
###解析数据包
def decodeINS(fDataBag):
    deviceLable = '' #标签号
    rebootCount = 0 #复位计数
    ticksolt = 0 #报警随即数，单次报警应不变
    msgBag = "缺省"
    if fDataBag[0:2] == '62':
        dataClass = fDataBag[2:4]
        match dataClass:
            case '1C': #报警包
                msgBag = "报警包"
                deviceLable = coverBig(fDataBag[4:12])
                rebootCount = hex2Int(fDataBag[12:16])
                ticksolt = hex2Int(fDataBag[16:20])
                warnType = fDataBag[24:26]
                warnMsg = ""
                match warnType:
                    case '01':
                        warnMsg = "按键报警"
                    case '02':
                        warnMsg = "按键取消确认"
                    case '03':
                        warnMsg = "跌落报警"
                    case '04':
                        pwarnMsg = "撞击报警"
                    case '05':
                        warnMsg = "脱帽检测"
                    case '07':
                        warnMsg = "心率异常"
                print(msgBag,"-设备标签-",deviceLable,"-重启数-",rebootCount,"-报警随机数-",ticksolt,"-报警信息-",warnMsg)
            case '22': #心跳包
                msgBag = "心跳包"
                deviceLable = coverBig(fDataBag[4:12]) # 标签号
                rebootCount = hex2Int(fDataBag[12:16]) # 复位计数
                soltid = hex2Int(fDataBag[16:20]) # soltid
                lableVersion = hex2Int(fDataBag[20:24]) # 手表版本
                lableS = fDataBag[24:26] # 手表状态,04表示休眠
                msgLableS = "缺省"
                match lableS:
                    case '01':
                        msgLableS = "按键报警"
                    case '02':
                        msgLableS = "下发报警"
                    case '04':
                        msgLableS = "休眠"
                lableE = hex2Int(fDataBag[26:28]) # 手表电压,默认上传百分比
                heartRate = -1000
                watchType = "缺省"
                bloodOxy = -1000
                bodyTemp = -1000
                bloodPreHigh = -1000
                bloodPreLow = -1000
                heat = -1000
                if fDataBag[96:98] == '0E': # 腕表类型
                    watchType = coverBig(fDataBag[98:102])
                if fDataBag[102:104] == '0F': # 生命体征1
                    heartRate = hex2Int(fDataBag[104:106])
                    bloodOxy = hex2Int(fDataBag[106:108])
                    bodyTemp = hex2Int(fDataBag[108:112])/10
                if fDataBag[112:114] == '10': #生命体征2
                    bloodPreHigh = hex2Int(fDataBag[114:116])
                    bloodPreLow = hex2Int(fDataBag[116:118])
                    heat = hex2Int(fDataBag[118:122])
                print(msgBag,"-设备标签-",deviceLable,"-重启数-",rebootCount,"-扫描周期-",soltid,"-手表版本-",lableVersion,
                      "-手表状态-",msgLableS,"-手表电压-",lableE,"%","-腕表类型-",watchType,"-心率-",heartRate,"-血氧-",bloodOxy,
                      "-体温-",bodyTemp,"-高压-",bloodPreHigh,"-低压-",bloodPreLow,"-热量-",heat)
            case '1D': #gps包
                msgBag = "gps包"
                deviceLable = coverBig(fDataBag[4:12]) # 标签号
                offset = hex2Int(fDataBag[12:14]) # 偏移阈值
                startNum = hex2Int(fDataBag[14:16]) # 搜索到的卫星数
                soltid = hex2Int(fDataBag[16:20]) # soltid
                longitude = hex2Int(fDataBag[20:28])*3600000 #经度
                latitude = hex2Int(fDataBag[28:36])*3600000 #纬度
                speed = hex2Int(fDataBag[36:40]) #当前移动速度
                altitude = hex2Int(fDataBag[42:46]) #海拔
                print(msgBag,"-设备标签-",deviceLable,"-偏移阈值-",offset,"-卫星数-",startNum,"-扫描周期-",soltid,
                      "-经度-",longitude,"-纬度-",latitude,"-移动速度-",speed,"-海拔-",altitude)
            case '24': #蓝牙
                msgBag = "蓝牙包"
                deviceLable = coverBig(fDataBag[4:12]) # 标签号
                soltid = hex2Int(fDataBag[12:16]) # soltid
                lableBleTime = int((len(fDataBag)-16)/12)
                bleMac = [] #信标mac地址
                bleRssi = [] #信标rssi
                bleVol = [] #信标电压
                print(msgBag,"-设备标签-",deviceLable,"-扫描周期-",soltid,"-蓝牙数-",lableBleTime)
                for i in range(lableBleTime):
                    mStr = fDataBag[16+i*12:16+i*12+12]
                    bleMac.append(coverBig(mStr[0:8]))
                    bleRssi.append(hex2Int(mStr[8:10]))
                    bleVol.append(hex2Int(mStr[10:12]))
                    print("-信标",i+1,"-","-mac-",bleMac[i],"-rssi-",bleRssi[i],"-电压-",bleVol[i])
                
            case '28': #gps+蓝牙
                msgBag = "gps+蓝牙包"
                print(msgBag)  


###将字符串翻转，因发送的数据小端在前
###
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
###未大小端转化的16进制的字符串转化为整数
###
def hex2Int(fHex):
    return int(coverBig(fHex),16)

###测试下发数据
def sendData(id):
    head1 = '88' # 协议格式
    head2 = '01' # 前缀标志
    paramsLen = '11' # 数据包长度
    flag = '00'
    cla = '13'
    ins = '03'
    hexId = '{:02X}'.format(id)
    slotid = hexId+'000000' # 记录序列号
    local = 'ffffffff' # 广播模式
    warnClass = '01' # 紧急撤离
    warnDisplay = '01' # 震动提醒
    warnTime = '03' # 报警时长
    id = '00000000' # 厂商编号，不匹配编号
    params = slotid+local+warnClass+warnDisplay+warnTime+id # 携带信息
    sendList = head1+head2+paramsLen+flag+cla+ins+params
    sendByte = bin(int(sendList,16))
    crc16 = crc16_ccitt(sendByte) # crc校验信息
    return sendList+crc16

def crc16_ccitt(data: bytes):
    crc16_ccitt_table_l =[
        0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf,
        0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7, 0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
        0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876, 0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd,
        0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5, 0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c,
        0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974, 0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb,
        0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3, 0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a,
        0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72, 0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9,
        0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1, 0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738,
        0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70, 0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7, 
        0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff, 0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036, 
        0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e, 0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5, 
        0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd, 0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134, 
        0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c, 0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3, 
        0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb, 0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232, 
        0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a, 0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1,
        0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9, 0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330, 
        0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78
    ]
    crc = 0x0000  # 初始值

    # 计算 CRC
    for byte in data:
        crc = (crc >> 8) ^ crc16_ccitt_table_l[(crc ^ byte) & 0xFF]

    return f"{crc & 0xFFFF:04x}"  # 只保留低 16 位
    

if __name__ == '__main__':
    print("udp server ")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定端口:
    # s.bind(('192.168.1.100', 3824))
    # main(s)
    for i in range(100):
        ss = sendData(i)
        ssbin = bin(int(ss,16))
        s.sendto(ss, ('192.168.1.200', 49152))
        time.sleep(10)
    
