#!/bin/bash

# ===== Usage =====
# LINE_TOKEN=xxx LINE_USER_ID=yyy OPENAI_API_KEY=zzz ./run_local.sh
# =================

# 如果 .credential.rc 存在，就 source 它
if [ -f .credential.rc ]; then
    echo "Sourcing .credential.rc..."
    source .credential.rc
fi

# 顯示遮蔽過的 token 值
echo "🔐 LINE_TOKEN: ${LINE_TOKEN:0:8}******"
echo "👤 LINE_USER_ID: ${LINE_USER_ID:0:8}******"
echo "🧠 OPENAI_API_KEY: ${OPENAI_API_KEY:0:8}******"

# 檢查必要環境變數
missing=0

if [ -z "$LINE_TOKEN" ]; then
  echo "❌ 缺少環境變數：LINE_TOKEN"
  missing=1
fi

if [ -z "$LINE_USER_ID" ]; then
  echo "❌ 缺少環境變數：LINE_USER_ID"
  missing=1
fi

if [ -z "$OPENAI_API_KEY" ]; then
  echo "❌ 缺少環境變數：OPENAI_API_KEY"
  missing=1
fi

if [ "$missing" -eq 1 ]; then
  echo "⚠️  請使用以下方式執行："
  echo "LINE_TOKEN=xxx LINE_USER_ID=yyy OPENAI_API_KEY=zzz ./run_local.sh"
  exit 1
fi

# 安裝依賴（多裝沒差）
pip install -q --disable-pip-version-check --no-warn-script-location -r requirements.txt
echo "Dependency checked"

# 執行主程式
python3 check_ticket.py
