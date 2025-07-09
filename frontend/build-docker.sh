#!/bin/bash

echo "🚀 开始构建优化的Docker镜像..."

# 构建镜像
docker build -t scada-frontend:optimized .

# 显示镜像大小
echo ""
echo "📊 镜像大小信息:"
docker images scada-frontend:optimized --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# 显示镜像层信息
echo ""
echo "🔍 镜像层分析:"
docker history scada-frontend:optimized

echo ""
echo "✅ 构建完成！"
echo "💡 优化建议:"
echo "   - 使用多阶段构建分离构建和运行环境"
echo "   - 启用Next.js standalone输出模式"
echo "   - 使用.dockerignore减少构建上下文"
echo "   - 使用非root用户提高安全性"
echo "   - 使用dumb-init处理信号" 