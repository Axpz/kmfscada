#!/bin/bash

# SSL证书管理脚本
# 用于生成、更新和验证SSL证书

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="$SCRIPT_DIR/../volumes/api/ssl"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    if ! command -v openssl &> /dev/null; then
        log_error "OpenSSL未安装"
        exit 1
    fi
    log_success "依赖检查通过"
}

# 创建SSL目录
create_ssl_dir() {
    log_info "创建SSL目录..."
    mkdir -p "$SSL_DIR"
    log_success "SSL目录已创建: $SSL_DIR"
}

# 生成CA证书
generate_ca() {
    log_info "生成CA证书..."
    
    if [ -f "$SSL_DIR/ca.key" ] && [ -f "$SSL_DIR/ca.crt" ]; then
        log_warning "CA证书已存在，跳过生成"
        return
    fi
    
    cd "$SSL_DIR"
    
    # 生成CA私钥
    openssl genrsa -out ca.key 2048
    log_info "CA私钥已生成"
    
    # 生成CA根证书
    openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=KMF/OU=SCADA/CN=KMF-CA"
    log_success "CA根证书已生成"
}

# 生成服务器证书
generate_server_cert() {
    log_info "生成服务器证书..."
    
    if [ ! -f "$SSL_DIR/ca.key" ] || [ ! -f "$SSL_DIR/ca.crt" ]; then
        log_error "CA证书不存在，请先生成CA证书"
        exit 1
    fi
    
    cd "$SSL_DIR"
    
    # 生成服务器私钥
    openssl genrsa -out mqtt.key 2048
    log_info "服务器私钥已生成"
    
    # 生成证书签名请求
    openssl req -new -key mqtt.key -out mqtt.csr \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=KMF/OU=SCADA/CN=localhost"
    log_info "证书签名请求已生成"
    
    # 使用CA签名服务器证书
    openssl x509 -req -days 365 -in mqtt.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out mqtt.crt
    log_success "服务器证书已生成"
    
    # 清理临时文件
    rm mqtt.csr
    log_info "临时文件已清理"
}

# 验证证书
verify_certs() {
    log_info "验证证书..."
    
    cd "$SSL_DIR"
    
    # 验证CA证书
    if openssl x509 -in ca.crt -text -noout &> /dev/null; then
        log_success "CA证书格式正确"
    else
        log_error "CA证书格式错误"
        return 1
    fi
    
    # 验证服务器证书
    if openssl x509 -in mqtt.crt -text -noout &> /dev/null; then
        log_success "服务器证书格式正确"
    else
        log_error "服务器证书格式错误"
        return 1
    fi
    
    # 验证服务器证书是否由CA签名
    if openssl verify -CAfile ca.crt mqtt.crt &> /dev/null; then
        log_success "服务器证书由CA正确签名"
    else
        log_error "服务器证书签名验证失败"
        return 1
    fi
    
    # 显示证书信息
    log_info "证书信息:"
    echo "CA证书:"
    openssl x509 -in ca.crt -text -noout | grep "Issuer\|Subject\|Not After"
    echo ""
    echo "服务器证书:"
    openssl x509 -in mqtt.crt -text -noout | grep "Issuer\|Subject\|Not After"
}

# 更新证书
renew_certs() {
    log_info "更新证书..."
    
    # 备份旧证书
    if [ -f "$SSL_DIR/mqtt.crt" ]; then
        cp "$SSL_DIR/mqtt.crt" "$SSL_DIR/mqtt.crt.backup"
        log_info "旧证书已备份"
    fi
    
    # 重新生成服务器证书
    generate_server_cert
    
    # 验证新证书
    verify_certs
    
    log_success "证书更新完成"
}

# 显示帮助信息
show_help() {
    echo "SSL证书管理脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  generate    生成CA和服务器证书"
    echo "  verify      验证证书"
    echo "  renew       更新服务器证书"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 generate    # 生成所有证书"
    echo "  $0 verify      # 验证证书"
    echo "  $0 renew       # 更新服务器证书"
}

# 主函数
main() {
    case "${1:-help}" in
        "generate")
            check_dependencies
            create_ssl_dir
            generate_ca
            generate_server_cert
            verify_certs
            log_success "证书生成完成"
            ;;
        "verify")
            verify_certs
            ;;
        "renew")
            renew_certs
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"
