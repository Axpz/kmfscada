# 首先设置LAN，确保跟PLC在同一个网段，如果不在，可以考虑添加路由
# 设置WAN，连接路由器到互联网
# 设置GPRS，添加sim卡，连接蜂窝网络
# 设置wifi，添加AP 和 STA两种模式，可选


# 可编程界面
1. 添加 #注入 作为trigger，触发式编程
2. 添加 #PING 作为 ping测试网络是否通畅
3. 添加 #调试 作为输出，查看输出加过
4. 添加 #函数计算，作为编程模块，支持javascript
5. 添加 #MQTT订阅，作为subscriber，可以配置远程
6. 添加 #MQTT发布，作为publisher，可以配置远程
7. 添加 #SIE Siemens, 作为plc下行采集模块，
        配置网络参数
        选择型号为S200Smart
        配置点位表，如果需要地址段优化，即同一块连续地址段一次读取，需要配置组，例如组a
        配置循环读取，采集频率，循环读取为-1时，不自动采集，大于1时为采集时间
8. 添加函数计算，支持编程添加时间戳
9. 使用拆分、过滤、合并函数计算，可以达到只发送有变化的数据

https://docs.qq.com/sheet/DREt1VWhSbXBzSENm?no_promotion=1&tab=BB08J2

https://docs.qq.com/doc/DRHVYaU5TQmVoa1Ju