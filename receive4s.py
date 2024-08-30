import socket
import json
import datetime

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定端口:
    s.bind(('192.168.1.2', 8050))
    while True:
        # 接收数据:
        data, addr = s.recvfrom(1024) # 最大字节数
        dataStr = data.decode("utf-8")
        dataJson = json.loads(dataStr)
        print("软件版本号:",dataJson["v"])
        print("电池电量:",dataJson["battery"])
        print("Mac 地址:",dataJson["mac"])
        print("SIM 卡号:",dataJson["qccid"])
        if dataJson["is_motion"] == 0:
            print("运动状态:静止")
        else:
            print("运动状态:移动")
        timeInt = int(dataJson["time"],16)
        timeDate = datetime.datetime.fromtimestamp(timeInt)
        print("数据生成时间:",timeDate)
        print("心率:",dataJson["hr"])
        print("血氧:",dataJson["spo2"])
        for i, device in enumerate(dataJson["devices"]):
            time2Int = int(device[0:8],16)
            time2Date = datetime.datetime.fromtimestamp(time2Int)
            print("信标:",i,"时间:",time2Date)
            print("信标:",i,"mac:",device[8:20])
            rssiInt = int(device[20:22],16)
            print("信标:",i,"Rssi:",rssiInt-256)
            powerInt = int(device[22:24],16)
            print("信标:",i,"电量:",powerInt)

if __name__ == '__main__':
    print("udp server ")
    main()
