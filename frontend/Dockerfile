# ---- 构建阶段:node 编译前端 ----
FROM node:20-alpine AS build
WORKDIR /app

# 先拷依赖清单,复用层缓存
COPY package.json package-lock.json ./
RUN npm ci

# 拷贝源码并构建;注入生产同源路径(经 nginx 反代 /api)
COPY . .
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# ---- 运行阶段:nginx 托管静态 + 反代 /api(REST 与 WS) ----
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
