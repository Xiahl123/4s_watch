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
                bloodOxy = -1000
                bodyTemp = -1000
                bloodPreHigh = -1000
                bloodPreLow = -1000
                heat = -1000
                if fDataBag[102:104] == '0F': # 生命体征1
                    heartRate = hex2Int(fDataBag[104:106])
                    bloodOxy = hex2Int(fDataBag[106:108])
                    bodyTemp = hex2Int(fDataBag[108:112])/10
                if fDataBag[112:114] == '10': #生命体征2
                    bloodPreHigh = hex2Int(fDataBag[114:116])
                    bloodPreLow = hex2Int(fDataBag[116:118])
                    heat = hex2Int(fDataBag[118:122])
                print(msgBag,"-设备标签-",deviceLable,"-重启数-",rebootCount,"-扫描周期-",soltid,"-手表版本-",lableVersion,
                      "-手表状态-",msgLableS,"-手表电压-",lableE,"%","-心率-",heartRate,"-血氧-",bloodOxy,
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
def sendData():
    head1 = '88' # 协议格式
    head2 = '01' # 前缀标志
    paramsLen = '11' # 数据包长度
    flag = '00'
    cla = '13'
    ins = '03'
    slotid = '00000012' # 记录序列号
    local = 'ffffffff' # 广播模式
    warnClass = '01' # 紧急撤离
    warnDisplay = '01' # 震动提醒
    warnTime = '03' # 报警时长
    id = '00000000' # 厂商编号，不匹配编号
    params = slotid+local+warnClass+warnDisplay+warnTime+id # 携带信息
    sendList = head1+head2+paramsLen+flag+cla+ins+params
    crc16 = '00' # crc校验信息
    return sendList+crc16


if __name__ == '__main__':
    print("udp server ")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定端口:
    s.bind(('192.168.1.100', 3824))
    main(s)
    ss = sendData()
    s.send(ss)
