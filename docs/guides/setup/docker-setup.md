# Docker 部署指南

## 配置Docker镜像加速器

由于网络原因，需要配置国内镜像源才能正常拉取镜像。

### macOS配置

1. 打开Docker Desktop
2. 点击设置图标 -> Docker Engine
3. 在JSON配置中添加：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

4. 点击 "Apply & Restart"

### 或者通过命令行配置

```bash
# 创建或编辑daemon.json
mkdir -p ~/.docker
cat > ~/.docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF

# 重启Docker Desktop
```

## 启动前端服务

配置好镜像加速器后：

```bash
# 在项目根目录执行
cd /Users/mac/Documents/ai/stock

# 构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f frontend

# 停止服务
docker-compose down
```

## 访问应用

前端服务启动后，访问：http://localhost:5173

## 常用命令

```bash
# 查看运行状态
docker-compose ps

# 重启服务
docker-compose restart frontend

# 查看实时日志
docker-compose logs -f frontend

# 进入容器
docker-compose exec frontend sh

# 停止并删除容器
docker-compose down

# 完全清理（包括镜像）
docker-compose down --rmi all -v
```

## 开发模式

由于使用了volume挂载，修改代码后会自动热更新，无需重启容器。

## 故障排查

### 端口被占用

```bash
# 查看5173端口占用
lsof -i :5173

# 杀掉占用进程
kill -9 <PID>
```

### 依赖安装失败

```bash
# 进入容器重新安装
docker-compose exec frontend sh
npm install
```

### 清理重建

```bash
# 停止并删除所有
docker-compose down -v

# 重新构建
docker-compose up -d --build
```
