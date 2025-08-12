@echo off
set /p MCP_ENDPOINT=wss://api.xiaozhi.me/mcp/?token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQzNDQyMiwiYWdlbnRJZCI6NTUyOTU5LCJlbmRwb2ludElkIjoiYWdlbnRfNTUyOTU5IiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc1NDkyMzQ0NX0._fa48iY9ysdXii2wI5BFmtRmiTkiV-ntFmBYDG1-_vgxrjeOvoN_yiJFF8lp_wnZ_g5AIaqZqOwii776JRACXg : 
echo MCP_ENDPOINT=%MCP_ENDPOINT% > .env
echo 已將 MCP_ENDPOINT 儲存到 .env
pip install -r requirements.txt
pip install playsound==1.2.2 requests
python mcp_pipe.py music.py
pause
