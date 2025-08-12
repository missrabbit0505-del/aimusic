#!/bin/bash
read -p "請輸入 MCP Endpoint（例如 wss://api.xiaozhi.me/mcp/?token=xxx）: " MCP_ENDPOINT
echo "MCP_ENDPOINT=$MCP_ENDPOINT" > .env
echo "已將 MCP_ENDPOINT 儲存到 .env"
pip install -r requirements.txt
pip install playsound==1.2.2 requests
python mcp_pipe.py music.py
