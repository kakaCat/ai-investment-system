# 本地开发环境搭建

## 前置要求

- Node.js 18+
- npm 或 pnpm

## 快速开始

### 1. 安装依赖

```bash
cd /Users/mac/Documents/ai/stock/frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

### 3. 访问应用

打开浏览器访问：http://localhost:5173

## 可用命令

```bash
# 开发模式（热更新）
npm run dev

# 类型检查并构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码格式化
npm run format

# 代码检查
npm run lint
```

## 开发说明

### 目录结构

```
frontend/
├── src/
│   ├── views/          # 页面组件
│   ├── components/     # 可复用组件
│   ├── router/         # 路由配置
│   ├── stores/         # Pinia状态管理
│   ├── types/          # TypeScript类型定义
│   ├── api/            # API请求
│   ├── utils/          # 工具函数
│   └── assets/         # 静态资源
├── public/             # 公共资源
└── mock/               # Mock数据
```

### 热更新

修改代码后浏览器会自动刷新，无需手动重启。

### Mock数据

当前所有功能都使用Mock数据，暂未对接真实后端API。

### 端口配置

默认端口：5173
如需修改，编辑 `vite.config.ts` 中的 `server.port`

## 构建生产版本

```bash
# 构建
npm run build

# 预览构建结果
npm run preview
```

构建产物在 `dist/` 目录。

## 故障排查

### 端口占用

```bash
# 查看5173端口占用
lsof -i :5173

# 杀掉占用进程（Mac/Linux）
kill -9 <PID>
```

### 依赖安装失败

```bash
# 清除缓存重新安装
rm -rf node_modules package-lock.json
npm install
```

### 使用国内镜像加速

```bash
# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 或者使用cnpm
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install
```

### TypeScript错误

```bash
# 重新生成类型声明文件
npm run dev
```

## 推荐开发工具

- **VS Code** + 以下插件：
  - Volar (Vue 3支持)
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense

## 环境变量

创建 `.env.local` 文件（已被.gitignore）：

```env
# API基础URL
VITE_API_BASE_URL=http://localhost:8000

# 其他配置...
```
