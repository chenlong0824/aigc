#!/bin/bash
# 咸阳文旅AIGC智能营销平台 - 升级脚本
# 用法: bash upgrade.sh

set -e

echo "========================================="
echo "咸阳文旅AIGC - 服务升级"
echo "========================================="

cd /opt/aigc

# 1. 拉取最新代码
echo ""
echo "[1/5] 拉取最新代码..."
git pull origin main

# 2. 安装模型到缓存目录（首次部署或更新模型时）
echo ""
echo "[2/5] 安装ONNX模型到缓存..."
MODEL_DIR="/root/.cache/chroma/onnx_models/all-MiniLM-L6-v2"
mkdir -p "$MODEL_DIR"
if [ -f "data/models/onnx_model.tar.gz" ]; then
    cp data/models/onnx_model.tar.gz "$MODEL_DIR/onnx.tar.gz"
    echo "  模型已安装到缓存 (from data/models/)"
elif [ -f "onnx_model.tar.gz" ]; then
    cp onnx_model.tar.gz "$MODEL_DIR/onnx.tar.gz"
    echo "  模型已安装到缓存 (from project root)"
elif [ -f "$MODEL_DIR/onnx.tar.gz" ]; then
    echo "  模型已缓存，跳过"
else
    echo "  模型文件不存在，将在首次使用时自动下载"
fi

# 3. 安装中文字体（FFmpeg 视频合成需要）
echo ""
echo "[3/6] 检查中文字体..."
if fc-list :lang=zh 2>/dev/null | grep -q .; then
    echo "  中文字体已安装"
else
    echo "  安装文泉驿微米黑..."
    apt-get update -qq && apt-get install -y -qq fonts-wqy-microhei 2>/dev/null
    fc-cache -fv 2>/dev/null
    echo "  中文字体安装完成"
fi

# 4. 安装Python依赖
echo ""
echo "[4/6] 检查Python依赖..."
if [ -f "backend/venv/bin/pip" ]; then
    backend/venv/bin/pip install -r backend/requirements.txt --quiet
    echo "  依赖已更新"
else
    echo "  跳过（venv不存在）"
fi

# 5. 构建前端
echo ""
echo "[5/7] 构建前端..."
if [ -f "frontend/package.json" ] && command -v npm &>/dev/null; then
    cd frontend
    npm install --silent 2>/dev/null
    npm run build 2>/dev/null
    cd ..
    echo "  前端构建完成"
else
    echo "  跳过（缺少npm或package.json）"
fi

# 6. 重启服务
echo ""
echo "[6/7] 重启服务..."
systemctl restart aigc-backend
sleep 3

# 7. 健康检查
echo ""
echo "[7/7] 健康检查..."
for i in $(seq 1 10); do
    STATUS=$(curl -s http://127.0.0.1:8000/api/health | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
    if [ "$STATUS" = "ok" ]; then
        echo "  服务运行正常!"
        break
    fi
    sleep 2
done

echo ""
echo "========================================="
echo "升级完成!"
echo "========================================="
