docker exec -it supabase-db psql -U postgres -d scada

\pset pager off


docker exec -it supabase-db psql -U supabase_admin -d scada

SELECT * FROM _supavisor.tenants LIMIT 10;
SELECT * FROM _supavisor.users LIMIT 10;

UPDATE auth.users SET raw_user_meta_data = jsonb_set(
  COALESCE(raw_user_meta_data, '{}'::jsonb),
  '{is_super_admin}',
  to_jsonb(is_super_admin),
  true
) WHERE is_super_admin IS NOT NULL;

UPDATE auth.users SET raw_user_meta_data = raw_user_meta_data - 'is_super_admin' WHERE raw_user_meta_data ? 'is_super_admin';

UPDATE auth.users SET raw_user_meta_data = raw_user_meta_data || '{"role": "super_admin"}'::jsonb
UPDATE auth.users SET raw_user_meta_data = raw_user_meta_data || '{"role": "admin"}'::jsonb


# display all functions
\df

# display all tables
\dt

# display all schemas
\dn


CREATE EXTENSION IF NOT EXISTS timescaledb;
SELECT * FROM pg_extension WHERE extname = 'timescaledb';

CREATE SCHEMA IF NOT EXISTS timeseries;
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'timeseries';



SELECT create_hypertable('public.sensor_readings', 'timestamp', if_not_exists => TRUE, migrate_data => TRUE);
SELECT set_chunk_time_interval('public.sensor_readings', INTERVAL '1 day');

SELECT * FROM timescaledb_information.hypertables;
SELECT * FROM timescaledb_information.dimensions;
SELECT * FROM timescaledb_information.chunks;


docker run --rm -p 5020:5020 topmaker/modsim

modpoll \
  --tcp localhost \
  --tcp-port 5020 \
  --config https://raw.githubusercontent.com/gavinying/modpoll/master/examples/modsim.csv

红色 1 火线
棕色 2 信号线
蓝色 3 接地


生产批号：VD 5000 4字节   Dword
  物料批号： 从生产批号摘取
当前直径：VW 5004 2字节 mm 00.000
当前温度：VW 500 2字节  short
            502 2字节
            504 2字节
            506 2字节
            508 2字节
            510 2字节
            512 2字节
            514 2字节
            516 2字节 备用


加温当前电流：VW 2字节
        VW 552 2字节
        VW 554 2字节
        7个区  45区
        8个区   55区

主机速度：VW 200 两个字节 螺杆速度
主机扭矩：VW 202
主机电流 VW 204
牵引当前速度：VW 206 两个字节 
真空当前速度：VW 208 两个字节



目标长度：VD1304 4个字节
当前长度：VD1332 4个字节


收捡机：
当前收卷速度：VW 104 2byte
       扭力：VW 106 2byte
    排管速度：VW 108 2byte

    排管层数：VW 500 4byte
    排管根数：VW 504 4byte



8月28日 mtqq 网关测试
1. 使用mqtt MQTT 5.0 协议
2. 使用mqtt 5.0 协议的客户端订阅主题
3. 使用mqtt 5.0 协议的客户端发布消息
4. 使用mqtt 5.0 协议的客户端断开连接
5. 使用mqtt 5.0 协议的客户端重新连接
6. 使用mqtt 5.0 协议的客户端重新订阅主题
7. 使用mqtt 5.0 协议的客户端重新发布消息


docker compose -f docker-compose.rabbitmq.yml up
    mosquitto_sub -h localhost -p 1883 -t test/topic -u admin -P admin123 -v -q 1
    mosquitto_sub -h localhost -p 1883 -t test/topic -u admin -P admin123 -v -q 1 -V mqttv5
    http://localhost:15672/#/queues

    mosquitto_pub -h localhost -p 1883 -t test/topic -m "hello world" -u admin -P admin123

    输出：
        mosquitto_sub -h localhost -p 1883 -t test/topic -u admin -P admin123 -v -q 1
        test/topic hello world

rabbitmq mqtt demo 测试通过

测试modpoll mqtt publish功能
docker run --rm -p 5020:5020 topmaker/modsim #启动modsim模拟器

modpoll \
  --tcp localhost \
  --tcp-port 5020 \
  --config https://raw.githubusercontent.com/gavinying/modpoll/master/examples/modsim.csv \
  --mqtt-host localhost \
  --mqtt-port 11883 \
  --mqtt-user admin \
  --mqtt-pass admin123 \
  --mqtt-publish-topic-pattern "test/topic" \
  --mqtt-qos 1

输出：
Device: modsim01
+---------------+-------------------------------------------------------+------+
| Reference     |                                                 Value | Unit |
+---------------+-------------------------------------------------------+------+
| coil01-08     | [True, False, False, False, False, True, False, True] |      |
| coil09-16     | [True, False, False, False, False, True, False, True] |      |
| di01-08       | [True, False, False, False, False, True, False, True] |      |
| di09-16       | [True, False, False, False, False, True, False, True] |      |
| input_reg01   |                                                     1 |      |
| input_reg02   |                                                     2 |      |
| input_reg03   |                                                     3 |      |
| input_reg04   |                                                     4 |      |
| input_reg05   |                                                    -1 |      |
| input_reg06   |                                                    -2 |      |
| input_reg07   |                                                    -3 |      |
| input_reg08   |                                                    -4 |      |
| input_reg09   |                                              12345678 |      |
| input_reg10   |                                             12345.678 |      |
| input_reg11   |                                             -12345678 |      |
| input_reg12   |                                        -12345678000.0 |      |
| input_reg13   |                                                 12.34 |      |
| input_reg14   |                                                -12.34 |      |
| holding_reg01 |                                                     1 |      |
| holding_reg02 |                                                     2 |      |
| holding_reg03 |                                                     3 |      |
| holding_reg04 |                                                     4 |      |
| holding_reg05 |                                                    -1 |      |
| holding_reg06 |                                                    -2 |      |
| holding_reg07 |                                                    -3 |      |
| holding_reg08 |                                                    -4 |      |
| holding_reg09 |                                              12345678 |      |
| holding_reg10 |                                             12345.678 |      |
| holding_reg11 |                                             -12345678 |      |
| holding_reg12 |                                        -12345678000.0 |      |
| holding_reg13 |                                                 12.34 |      |
| holding_reg14 |                                                -12.34 |      |
| holding_reg15 |                                           12345678900 |      |
| holding_reg16 |                                          -12345678900 |      |
| holding_reg17 |                                                123.45 |      |
| holding_reg18 |                                               -123.45 |      |
| holding_reg19 |                                      this is a string |      |
+---------------+-------------------------------------------------------+------+
2025-08-27 14:48:28,968 | I | modpoll.mqtt_task | Publish message to topic: test/topic

mosquitto_sub -h localhost -p 11883 -t test/topic -u admin -P admin123 -v -q 1 -V mqttv5
输出：
test/topic {"coil01-08": [true, false, false, false, false, true, false, true], "coil09-16": [true, false, false, false, false, true, false, true], "di01-08": [true, false, false, false, false, true, false, true], "di09-16": [true, false, false, false, false, true, false, true], "input_reg01": 1, "input_reg02": 2, "input_reg03": 3, "input_reg04": 4, "input_reg05": -1, "input_reg06": -2, "input_reg07": -3, "input_reg08": -4, "input_reg09": 12345678, "input_reg10": 12345.678, "input_reg11": -12345678, "input_reg12": -12345678000.0, "input_reg13": 12.34, "input_reg14": -12.34, "holding_reg01": 1, "holding_reg02": 2, "holding_reg03": 3, "holding_reg04": 4, "holding_reg05": -1, "holding_reg06": -2, "holding_reg07": -3, "holding_reg08": -4, "holding_reg09": 12345678, "holding_reg10": 12345.678, "holding_reg11": -12345678, "holding_reg12": -12345678000.0, "holding_reg13": 12.34, "holding_reg14": -12.34, "holding_reg15": 12345678900, "holding_reg16": -12345678900, "holding_reg17": 123.45, "holding_reg18": -123.45, "holding_reg19": "this is a string"}


# 测试rabbitmq 
make mqtt-ssl
mosquitto_sub -h localhost -p 8883 -t test/topic -u admin -P admin123 -v -q 1 -V mqttv5 --cafile volumes/api/ssl/ca.crt -d
mosquitto_pub -h localhost -p 8883 -t test/topic -m "hello" -u admin -P admin123 --cafile volumes/api/ssl/ca.crt

docker exec kmf-rabbitmq rabbitmqctl import_definitions  /etc/rabbitmq/definitions.json

