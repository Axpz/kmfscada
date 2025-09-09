from pymodbus.client import ModbusTcpClient

# =====================
# 配置设备信息
# =====================
PLC_IP = "192.168.1.6"  # 你的PLC IP
PLC_PORT = 80           # Modbus TCP 默认端口
UNIT_ID = 1              # 从站地址

# 创建 Modbus TCP 客户端
client = ModbusTcpClient(PLC_IP, port=PLC_PORT)

# 连接 PLC
if not client.connect():
    print("无法连接到 PLC")
    exit(1)

print("连接成功！")

# =====================
# 读取输入寄存器
# =====================
# input_start = 5004
# input_count = 2
# input_result = client.read_input_registers(input_start, input_count, unit=UNIT_ID)

# if input_result.isError():
#     print("读取输入寄存器失败:", input_result)
# else:
#     print("输入寄存器值:", input_result.registers)

# =====================
# 读取保持寄存器示例
# =====================
start_address = 5000    # 起始寄存器地址
count = 2          # 读取寄存器数量

result = client.read_holding_registers(start_address, count, unit=UNIT_ID)

if result.isError():
    print("读取保持寄存器失败:", result)
else:
    print("保持寄存器值:", result.registers)

# # =====================
# # 读取线圈示例
# # =====================
# coil_start = 0
# coil_count = 8

# coil_result = client.read_coils(coil_start, coil_count, unit=UNIT_ID)
# if coil_result.isError():
#     print("读取线圈失败:", coil_result)
# else:
#     print("线圈状态:", coil_result.bits)


# =====================
# 关闭连接
# =====================
client.close()
