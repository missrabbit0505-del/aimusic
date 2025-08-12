from mcp.server.fastmcp import FastMCP
import requests
from playsound import playsound
import tempfile
import os
import logging
import threading

mcp = FastMCP("MusicPlayer")
logger = logging.getLogger(__name__)
_LOCK = threading.Lock()

_API_URL = 'https://api.yaohud.cn/api/music/wy'
_API_KEY = '93R6TfntYUBXGg5W78X'  # 請填入你的API_KEY

@mcp.tool()
def play_music(song_name: str) -> str:
    if not song_name.strip():
        return "錯誤：歌曲名不能為空"

    with _LOCK:
        try:
            logger.info(f"搜索歌曲: {song_name}")
            params = {'key': _API_KEY, 'msg': song_name.strip(), 'n': '1'}
            resp = requests.post(_API_URL, params=params, timeout=10)
            resp.raise_for_status()
            music_url = resp.json()['data']['musicurl']

            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                f.write(requests.get(music_url, timeout=10).content)
                temp_path = f.name

            playsound(temp_path)
            os.unlink(temp_path)
            return f"播放成功: {song_name}"

        except Exception as e:
            logger.error(f"播放失敗: {str(e)}")
            return f"播放失敗: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
