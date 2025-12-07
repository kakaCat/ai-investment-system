#!/bin/bash

# 重启开发服务

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "🔄 重启服务..."
echo ""

# 停止现有服务
"$SCRIPT_DIR/stop.sh"

# 等待停止完成
sleep 2

# 启动服务
"$SCRIPT_DIR/dev.sh"
