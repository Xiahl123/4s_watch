import json
import base64
from datetime import datetime, timezone,timedelta
import struct
def convert_endian(hex_str):
    # 将十六进制字符串转换为字节
    byte_data = bytes.fromhex(hex_str)
    
    # 反转字节序列,大小端转换
    reversed_bytes = byte_data[::-1]
    # 将反转后的字节序列转换回十六进制字符串
    reversed = reversed_bytes.hex()
    # 转为int
    return int(reversed,16)

# 连接成功回调函数
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("application/fd83bd58-d6c5-4a37-8b44-d8bba21a8e75/device/013223228a35098d/event/up")

# 解码函数
def parse_encoded_string(encoded_str):
    # Decode the Base64 string
    decoded_bytes = base64.b64decode(encoded_str)
    
    # Convert the bytes to a hex string
    hex_str = decoded_bytes.hex()
    
    return hex_str


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

    return {
        "timestamp": timestamp_value,
        "parsed_data": parsed_data
    }



# 睡眠解析函数 有点问题
def parse_payload(hex_string):
    # Skip the first 4 bytes (BDC5)
    payload = hex_string[4:]
    
    # Convert hex string to bytes
    byte_data = bytes.fromhex(payload)

    # Unpack the data
    start_time, end_time, sleep_minutes, sleep_type = struct.unpack('>IIHI', byte_data)
    
    # Convert timestamps to human-readable format
    start_time = datetime.utcfromtimestamp(start_time)
    end_time = datetime.utcfromtimestamp(end_time)
    # Return the parsed data
    return_data= {
        "sleep_type": {1: "深度睡眠", 2: "浅睡眠", 3: "醒来时长"}.get(sleep_type, "未知"),
        "start_time": start_time,
        "end_time": end_time,
        "duration_minutes": sleep_minutes
    }
    print(f"睡眠状态为{return_data["sleep_type"]},开始时间为{return_data["start_time"]},结束时间为{return_data['end_time']},时长{return_data['duration_minutes']}分钟")


if __name__ == '__main__':
  a = '{"deduplicationId":"61fb3df0-c165-4a16-836f-3c3a2ec03208","time":"2024-09-03T11:00:21.177652+00:00","deviceInfo":{"tenantId":"52f14cd4-c6f1-4fbd-8f87-4025e1d49242","tenantName":"ChirpStack","applicationId":"fd83bd58-d6c5-4a37-8b44-d8bba21a8e75","applicationName":"application","deviceProfileId":"58163c18-87da-40c9-bf54-b91448ea9043","deviceProfileName":"device-profile","deviceName":"4s_device","devEui":"013223228a35098d","deviceClassEnabled":"CLASS_A","tags":{}},"devAddr":"01a45fb1","adr":true,"dr":3,"fCnt":11,"fPort":10,"confirmed":true,"data":"vdYAAaP21mEDRSfvmNFFJ6Gbx0UnepuwNL35AQIAAGQAAJMAAACj9tZhfw==","rxInfo":[{"gatewayId":"40d63cfffe7e41ea","uplinkId":946,"gwTime":"2024-09-03T11:00:21.177652+00:00","nsTime":"2024-09-03T11:00:21.245991628+00:00","rssi":-42,"snr":12.75,"channel":5,"rfChain":1,"location":{},"context":"o6wwjA==","metadata":{"region_common_name":"AS923","region_config_id":"as923"},"crcStatus":"CRC_OK"}],"txInfo":{"frequency":924200000,"modulation":{"lora":{"bandwidth":125000,"spreadingFactor":9,"codeRate":"CR_4_5"}}}}'
  dataJson = json.loads(a)
#   data1 = bytes.fromhex("bd326d4a4c60220168010000000001642510d7614f")
#   parse_protocol(data1)
# Example usage
  str="bd3200f19acf6111000a000011573154397a1a6501220401416151bdf90103000064000000000000f19acf6126"
  data = bytes.fromhex(str[:50])
  result = parse_protocol(data)
  print(result)
  data = parse_encoded_string(dataJson['data'])
  print('hex:',data)
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
                print("健康")
                
            case 'c5':
                print("睡眠")
            case 'cb':
                print("天气")
                #c3f01999-4b66-4800-b6f4-3fe5ee61fcaa