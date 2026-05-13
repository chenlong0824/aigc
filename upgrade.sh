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
    echo "  模型已安装到缓存"
else
    echo "  模型文件不存在，将在首次使用时自动下载"
fi

# 3. 安装Python依赖
echo ""
echo "[3/5] 检查Python依赖..."
./venv/bin/pip install -r requirements.txt --quiet

# 4. 重启服务
echo ""
echo "[4/5] 重启服务..."
systemctl restart aigc-backend
sleep 3

# 5. 健康检查
echo ""
echo "[5/5] 健康检查..."
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
