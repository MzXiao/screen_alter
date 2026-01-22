#!/bin/bash

# 1. 定义变量（方便后续维护）
IMAGE_NAME="crpi-qpp3zee61k91dpmz.cn-shanghai.personal.cr.aliyuncs.com/xiaominz/screen_alter_backend:v1"
CONTAINER_NAME="screen_alter_backend"

echo "开始执行更新流程..."

# 2. 拉取最新镜像
echo "正在从仓库拉取最新镜像: $IMAGE_NAME"
docker pull $IMAGE_NAME

# 3. 停止并删除旧容器（如果存在）
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "发现正在运行或残留的容器，正在停止并删除..."
    docker rm -f $CONTAINER_NAME
fi

# 4. 运行新容器 (直接复用你 start.sh 中的配置)
echo "正在启动新容器..."
docker run -d \
  --name $CONTAINER_NAME \
  -p 8100:8000 \
  --add-host host.docker.internal:host-gateway \
  --restart always \
  -e TZ=Asia/Shanghai \
  $IMAGE_NAME

echo "容器已重启！"
docker ps -f name=$CONTAINER_NAME