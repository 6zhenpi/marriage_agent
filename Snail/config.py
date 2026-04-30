import os
from pathlib import Path

PROJECT_ROOT = Path(r"d:\project\marriage_agent")
DATA_ROOT = PROJECT_ROOT / "Collected legal data"
LOG_DIR = Path(__file__).parent / "logs"

REQUEST_DELAY_MIN = 3.0
REQUEST_DELAY_MAX = 6.0
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2.0

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
]

PROXY_ENABLED = os.getenv("SNAIL_PROXY_ENABLED", "false").lower() == "true"
PROXY_URL = os.getenv("SNAIL_PROXY_URL", "")

SOURCES = {
    "law_npc": {
        "name": "国家法律法规数据库",
        "base_url": "https://flk.npc.gov.cn",
        "enabled": True,
        "respect_robots": True,
    },
    "law_court": {
        "name": "最高人民法院官网",
        "base_url": "https://www.court.gov.cn",
        "enabled": True,
        "respect_robots": True,
    },
    "case_rmfyalk": {
        "name": "人民法院案例库",
        "base_url": "https://rmfyalk.court.gov.cn",
        "enabled": True,
        "respect_robots": True,
    },
    "law_12348": {
        "name": "12348中国法网",
        "base_url": "https://www.12348.gov.cn",
        "enabled": True,
        "respect_robots": True,
    },
}
