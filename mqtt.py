import paho.mqtt.client as mqtt
import json
import base64
from datetime import datetime, timezone
def convert_endian(hex_str):
    # 将十六进制字符串转换为字节
    byte_data = bytes.fromhex(hex_str)
    
    # 反转字节序列
    reversed_bytes = byte_data[::-1]
    reversed = reversed_bytes.hex()

    # 将反转后的字节序列转换回十六进制字符串
    return int(reversed,16)

# 连接成功回调函数
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("application/fd83bd58-d6c5-4a37-8b44-d8bba21a8e75/device/013223228a35098d/event/up")

# 转化为格林尼治时间
def timestamp_to_utc(timestamp):
    # Convert timestamp to UTC datetime
    utc_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return utc_time.strftime('%Y-%m-%d %H:%M:%S %Z')
# 蓝牙协议解析函数
def parse_data(data):
    data_bytes = bytes.fromhex(data)
    total_groups = data_bytes[3]
    
    index = 4
    
    for group in range(total_groups):
        timestamp = int.from_bytes(data_bytes[index:index + 4], byteorder='little')
        index += 4
        
        beacon_count = data_bytes[index]
        index += 1
        
        beacons = []
        for _ in range(beacon_count):
            major = int.from_bytes(data_bytes[index:index + 2], byteorder='little')
            index += 2
            
            minor = int.from_bytes(data_bytes[index:index + 2], byteorder='little')
            index += 2
            
            rssi = int.from_bytes(data_bytes[index:index + 1], byteorder='little', signed=True)
            index += 1
            
            beacons.append({
                'major': major,
                'minor': minor,
                'rssi': rssi
            })
        
        print(f"  Group {group + 1}:")
        print(f"    Timestamp: {timestamp_to_utc(timestamp)}")
        for beacon in beacons:
            print(f"    Major: {beacon['major']}, Minor: {beacon['minor']}, RSSI: {beacon['rssi']}")


# 健康解析函数
def parse_protocol(data):
    # Helper function to convert bytes to integer
    def bytes_to_int(byte_data):
        return int.from_bytes(byte_data, byteorder='little')

    # Check if data length is sufficient
    if len(data) < 8:
        raise ValueError("Data is too short to contain a valid message")

    # Parse timestamp
    timestamp = data[2:6]
    timestamp_value = bytes_to_int(timestamp)

    # Parse total length (excluding checksum)
    total_length = bytes_to_int(data[6:8])

    # Initialize index to start parsing data
    index = 8
    parsed_data = {}

    # Data ID mapping
    data_id_mapping = {
        0x01: "步数",
        0x02: "心率",
        0x03: "体温",
        0x04: "腕温",
        0x05: "血糖",
        0x06: "舒张压",
        0x07: "收缩压",
        0x08: "血氧",
    }

    while index < len(data) - 1:  # Avoid checksum byte
        # Get ID and length
        id_length_byte = data[index]
        data_id = (id_length_byte >> 3) & 0x1F
        data_length = id_length_byte & 0x07

        # Ensure there is enough data left to read
        if index + 1 + data_length > len(data) - 1:
            raise ValueError("Data is too short for the specified length")

        # Read data value
        data_value_bytes = data[index + 1:index + 1 + data_length]
        data_value = bytes_to_int(data_value_bytes)

        # Map ID to human-readable description
        if data_id in data_id_mapping:
            parsed_data[data_id_mapping[data_id]] = data_value

        # Move index to next data block
        index += 1 + data_length

    print(parsed_data)
    # return {
    #     "timestamp": timestamp_value,
    #     "parsed_data": parsed_data
    # }

# 消息接收回调函数
def on_message(client, userdata, msg):
    dataJson = json.loads(msg.payload)
    data = parse_encoded_string(dataJson['data'])
    dataHead = data[0:2]
    if dataHead == 'bd':
        dataType = data[2:4]
        match dataType:
            case 'f9':
                power = data[12:16]
                powerInt = convert_endian(power)
                print("电量:",powerInt)
            case '02':
                warnHex = data[4:8]
                warnInt = convert_endian(warnHex)
                match warnInt:
                    case 16384:
                        print("跌落报警")
                    case 256:
                        print("设备佩戴")
                    case 128:
                        print("SOS取消")
                    case 32:
                        print("久坐报警")
                    case 16:
                        print("摘掉设备")
                    case 4:
                        print("关机")
                    case 2:
                        print("SOS")
                    case 1:
                        print("低电量")
            case '03':
                print("GPS")
            case 'd6':
                print("蓝牙定位:")
                parse_data(data)
            case 'c3':
                print("充电")
                power_status=data[4:6]
                match power_status:
                  case "00":
                        print("设备开始充电")
                  case "01":
                        print("设备结束充电")
                  case "02":
                        print("设备已充满电")
            case '32':
                print("健康:")
                str=data[:50]
                data1=bytes.fromhex(str)
                parse_protocol(data1)
            case 'c5':
                print("睡眠")
            case 'cb':
                print("天气")
            case 'b5':
                print('SOS')
                
    # print(msg.topic + " " + str(data))

# 解码函数
def parse_encoded_string(encoded_str):
    # Decode the Base64 string
    decoded_bytes = base64.b64decode(encoded_str)
    
    # Convert the bytes to a hex string
    hex_str = decoded_bytes.hex()
    
    return hex_str

if __name__ == '__main__':
    # 创建客户端实例
    client = mqtt.Client()

    # 设置连接成功和消息接收的回调函数
    client.on_connect = on_connect
    client.on_message = on_message

    # 连接到 MQTT 代理
    client.connect("192.168.9.101", 1883, 60)

    # 循环处理网络流量
    client.loop_forever()