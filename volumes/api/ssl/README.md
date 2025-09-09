# SSL证书配置说明

## 目录结构
```
volumes/api/ssl/
├── README.md
├── mqtt.crt          # MQTT服务器证书（由CA签名）
├── mqtt.key          # MQTT私钥
├── ca.crt            # CA根证书
├── ca.key            # CA私钥
└── ca.srl            # CA序列号文件
```

## 生成CA和服务器证书

### 1. 生成CA私钥和证书
```bash
# 生成CA私钥
openssl genrsa -out ca.key 2048

# 生成CA根证书
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=KMF/OU=SCADA/CN=KMF-CA"
```

### 2. 生成服务器私钥
```bash
openssl genrsa -out mqtt.key 2048
```

### 3. 生成服务器证书签名请求
```bash
openssl req -new -key mqtt.key -out mqtt.csr \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=KMF/OU=SCADA/CN=mqtt.localhost"
```

### 4. 使用CA签名服务器证书
```bash
openssl x509 -req -days 365 -in mqtt.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out mqtt.crt
```

### 5. 清理临时文件
```bash
rm mqtt.csr
```

## 使用Let's Encrypt证书

如果您有Let's Encrypt证书，可以直接复制到此处：
```bash
# 复制Let's Encrypt证书
cp /path/to/your/cert.pem mqtt.crt
cp /path/to/your/privkey.pem mqtt.key

# 复制Let's Encrypt CA证书（通常是chain.pem）
cp /path/to/your/chain.pem ca.crt
```

## 证书验证

验证证书是否正确：
```bash
# 查看服务器证书
openssl x509 -in mqtt.crt -text -noout

# 查看CA证书
openssl x509 -in ca.crt -text -noout

# 验证服务器证书是否由CA签名
openssl verify -CAfile ca.crt mqtt.crt
```

## 安全注意事项

1. 在生产环境中使用正式的SSL证书
2. 定期更新证书
3. 保护私钥文件的安全
4. 使用强密码保护私钥
