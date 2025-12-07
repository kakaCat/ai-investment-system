#!/bin/bash

echo "🚀 开始初始化前端项目..."
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未检测到 Node.js，请先安装 Node.js"
    exit 1
fi

echo "✓ Node.js 版本: $(node -v)"
echo "✓ npm 版本: $(npm -v)"
echo ""

# 检查是否在 frontend 目录
if [ ! -f "package.json" ]; then
    echo "❌ 请在 frontend 目录下运行此脚本"
    exit 1
fi

# 安装依赖
echo "📦 安装项目依赖..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo ""
echo "✅ 前端项目初始化完成！"
echo ""
echo "📝 下一步："
echo "  1. 启动开发服务器: npm run dev"
echo "  2. 浏览器访问: http://localhost:3000"
echo "  3. 默认路由: /account/list (账户列表)"
echo ""
echo "💡 提示："
echo "  - 当前使用 Mock 数据，无需启动后端"
echo "  - 登录页面任意用户名密码即可登录"
echo "  - 查看 README.md 了解更多信息"
echo ""
