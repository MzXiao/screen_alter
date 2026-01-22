#!/bin/bash

# Configuration
ALIYUN_REGISTRY="crpi-qpp3zee61k91dpmz.cn-shanghai.personal.cr.aliyuncs.com"
ALIYUN_NAMESPACE="xiaominz"
IMAGE_NAME="screen_alter_backend"
IMAGE_TAG="v1"
FULL_IMAGE_NAME="${ALIYUN_REGISTRY}/${ALIYUN_NAMESPACE}/${IMAGE_NAME}:${IMAGE_TAG}"

# Ensure we are in the project root
# If script is run from scripts/, move up; if from root, stay.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "Building Docker image from $PROJECT_ROOT..."

# Build the image
# Using linux/amd64 platform as requested
docker build --platform linux/amd64 -t "${FULL_IMAGE_NAME}" .

if [ $? -eq 0 ]; then
    echo "Build successful."
else
    echo "Build failed."
    exit 1
fi

echo "Logging in to Aliyun Registry..."
# Note: ALIYUN_USERNAME and ALIYUN_PASSWORD should be set in environment or user will be prompted/logged in if already cached.
# If explicit login is needed, user should ensure these vars are exported before running, or we can prompt.
# For this script based on user snippet, we assume environment or manual handling if variables aren't set, 
# but the snippet showed specific credentials. 
# SECURITY WARNING: Hardcoding passwords in scripts is bad practice. 
# However, the user explicitly provided them in the prompt. 
# I will use variables but default to what they provided if not set, or just use what they provided if that's acceptable context.
# Better to expect them as env vars for security, but user snippet had them inline.
# Let's use the Values provided by user but allow override.

: "${ALIYUN_USERNAME:=xiaominz}"
# Ideally password should not be here, but user pasted it. I will keep it in variables for now to match their workflow but maybe better to ask them to export it.
# Actually, the user's snippet was:
# ALIYUN_PASSWORD="mFGfX7MzWbSQAft"
# echo "${ALIYUN_PASSWORD}" | docker login ...
# I will include this structure but perhaps comment it out or put it in a separate auth block or just use variables.

: "${ALIYUN_PASSWORD:=mFGfX7MzWbSQAft}"

echo "${ALIYUN_PASSWORD}" | docker login --username "${ALIYUN_USERNAME}" --password-stdin "${ALIYUN_REGISTRY}"

if [ $? -eq 0 ]; then
    echo "Login successful."
else
    echo "Login failed."
    exit 1
fi

echo "Pushing image to registry..."
docker push "${FULL_IMAGE_NAME}"

if [ $? -eq 0 ]; then
    echo "Push successful."
    echo "Deploying to remote server 8.134.58.148..."
    
    REMOTE_HOST="root@8.134.58.148"
    CONTAINER_NAME="screen_alter_backend"
    
    ssh "${REMOTE_HOST}" "
        echo 'Pulling latest image...'
        docker pull ${FULL_IMAGE_NAME}
        
        if [ \"\$(docker ps -aq -f name=${CONTAINER_NAME})\" ]; then
            echo 'Stopping and removing old container...'
            docker rm -f ${CONTAINER_NAME}
        fi
        
        echo 'Starting new container...'
        docker run -d \\
          --name ${CONTAINER_NAME} \\
          -p 8100:8000 \\
          --add-host host.docker.internal:host-gateway \\
          --restart always \\
          -e TZ=Asia/Shanghai \\
          ${FULL_IMAGE_NAME}
          
        echo 'Waiting for container to start...'
        sleep 5
        
        if [ \"\$(docker ps -q -f name=${CONTAINER_NAME} -f status=running)\" ]; then
            echo 'Deployment successful! Container is running.'
        else
            echo 'Deployment failed! Container is not running.'
            docker logs ${CONTAINER_NAME}
            exit 1
        fi
        
        docker ps -f name=${CONTAINER_NAME}
    "
else
    echo "Push failed."
    exit 1
fi
