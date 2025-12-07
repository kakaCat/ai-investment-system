# 使用阿里云镜像仓库的Node.js镜像
FROM registry.cn-hangzhou.aliyuncs.com/library/node:20-alpine

# 设置工作目录
WORKDIR /app

# 设置npm镜像源为淘宝镜像
RUN npm config set registry https://registry.npmmirror.com

# 复制package.json和package-lock.json（如果存在）
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制项目文件
COPY . .

# 暴露Vite开发服务器端口
EXPOSE 5173

# 启动开发服务器
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
