#!/bin/bash

# Docker镜像加速器配置脚本
# 适用于 macOS Docker Desktop

echo "==================================================="
echo "Docker 镜像加速器配置脚本"
echo "==================================================="
echo ""

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker Desktop"
    exit 1
fi

echo "✅ Docker正在运行"
echo ""

# 创建配置目录
mkdir -p ~/.docker

# 配置文件路径
CONFIG_FILE=~/.docker/daemon.json

# 检查是否已有配置
if [ -f "$CONFIG_FILE" ]; then
    echo "⚠️  检测到已有配置文件: $CONFIG_FILE"
    echo "备份原配置到: ${CONFIG_FILE}.backup"
    cp "$CONFIG_FILE" "${CONFIG_FILE}.backup"
fi

# 写入新配置
cat > "$CONFIG_FILE" <<'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  }
}
EOF

echo "✅ 配置文件已创建: $CONFIG_FILE"
echo ""
echo "配置内容："
cat "$CONFIG_FILE"
echo ""
echo "==================================================="
echo "⚠️  重要提示："
echo "==================================================="
echo ""
echo "对于 Docker Desktop (macOS)，你需要："
echo ""
echo "1. 打开 Docker Desktop 应用"
echo "2. 点击右上角 ⚙️ (设置) 图标"
echo "3. 选择左侧菜单 'Docker Engine'"
echo "4. 在 JSON 配置中添加以下内容："
echo ""
echo '  "registry-mirrors": ['
echo '    "https://docker.mirrors.ustc.edu.cn",'
echo '    "https://hub-mirror.c.163.com",'
echo '    "https://mirror.baidubce.com"'
echo '  ]'
echo ""
echo "5. 点击 'Apply & Restart' 按钮"
echo ""
echo "==================================================="
echo "等待Docker重启后，运行以下命令验证："
echo "  docker info | grep -A 5 'Registry Mirrors'"
echo "==================================================="
