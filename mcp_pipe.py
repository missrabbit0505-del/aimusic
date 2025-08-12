import asyncio
import websockets
import subprocess
import logging
import os
import signal
import sys
import random
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MCP_PIPE')

INITIAL_BACKOFF = 1
MAX_BACKOFF = 60
reconnect_attempt = 0
backoff = INITIAL_BACKOFF

async def connect_with_retry(uri):
    global reconnect_attempt, backoff
    while True:
        try:
            if reconnect_attempt > 0:
                wait_time = backoff * (1 + random.random() * 0.1)
                logger.info(f"等待 {wait_time:.2f} 秒後重新連線 (第 {reconnect_attempt} 次)...")
                await asyncio.sleep(wait_time)
            await connect_to_server(uri)
        except Exception as e:
            reconnect_attempt += 1
            logger.warning(f"連線關閉 (第 {reconnect_attempt} 次): {e}")
            backoff = min(backoff * 2, MAX_BACKOFF)

async def connect_to_server(uri):
    global reconnect_attempt, backoff
    try:
        logger.info(f"正在連線到 WebSocket 伺服器...")
        async with websockets.connect(uri) as websocket:
            logger.info(f"已連線到 WebSocket 伺服器")
            reconnect_attempt = 0
            backoff = INITIAL_BACKOFF
            process = subprocess.Popen(
                ['python', mcp_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.info(f"已啟動 {mcp_script}")
            await asyncio.gather(
                pipe_websocket_to_process(websocket, process),
                pipe_process_to_websocket(process, websocket),
                pipe_process_stderr_to_terminal(process)
            )
    except Exception as e:
        logger.error(f"連線錯誤: {e}")
        raise
    finally:
        if 'process' in locals():
            logger.info(f"正在關閉 {mcp_script} 程式")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            logger.info(f"{mcp_script} 已關閉")

async def pipe_websocket_to_process(websocket, process):
    try:
        while True:
            message = await websocket.recv()
            logger.debug(f"<< {message[:120]}...")
            if isinstance(message, bytes):
                message = message.decode('utf-8')
            process.stdin.write(message + '\n')
            process.stdin.flush()
    except Exception as e:
        logger.error(f"WebSocket → 程式 錯誤: {e}")
        raise
    finally:
        if not process.stdin.closed:
            process.stdin.close()

async def pipe_process_to_websocket(process, websocket):
    try:
        while True:
            data = await asyncio.get_event_loop().run_in_executor(None, process.stdout.readline)
            if not data:
                logger.info("程式已停止輸出")
                break
            logger.debug(f">> {data[:120]}...")
            await websocket.send(data)
    except Exception as e:
        logger.error(f"程式 → WebSocket 錯誤: {e}")
        raise

async def pipe_process_stderr_to_terminal(process):
    try:
        while True:
            data = await asyncio.get_event_loop().run_in_executor(None, process.stderr.readline)
            if not data:
                logger.info("程式已停止錯誤輸出")
                break
            sys.stderr.write(data)
            sys.stderr.flush()
    except Exception as e:
        logger.error(f"錯誤輸出管道錯誤: {e}")
        raise

def signal_handler(sig, frame):
    logger.info("收到中斷信號，正在關閉...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    if len(sys.argv) < 2:
        logger.error("用法: mcp_pipe.py <mcp_script>")
        sys.exit(1)
    mcp_script = sys.argv[1]
    endpoint_url = os.environ.get('MCP_ENDPOINT')
    if not endpoint_url:
        logger.error("請設定 MCP_ENDPOINT 環境變數")
        sys.exit(1)
    try:
        asyncio.run(connect_with_retry(endpoint_url))
    except KeyboardInterrupt:
        logger.info("使用者中斷程式")
    except Exception as e:
        logger.error(f"執行錯誤: {e}")
