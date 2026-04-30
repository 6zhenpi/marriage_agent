import time
import random
import logging
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from Snail.config import (
    REQUEST_DELAY_MIN,
    REQUEST_DELAY_MAX,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_BACKOFF_FACTOR,
    USER_AGENTS,
    PROXY_ENABLED,
    PROXY_URL,
)

logger = logging.getLogger("snail.request_helper")


def _build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    if PROXY_ENABLED and PROXY_URL:
        session.proxies = {"http": PROXY_URL, "https": PROXY_URL}
        logger.info(f"Proxy enabled: {PROXY_URL}")

    return session


_session = _build_session()


def get(
    url: str,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: int = REQUEST_TIMEOUT,
    delay: bool = True,
) -> requests.Response:
    if delay:
        wait = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
        logger.debug(f"Rate limit: sleeping {wait:.1f}s before request")
        time.sleep(wait)

    final_headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    if headers:
        final_headers.update(headers)

    logger.info(f"GET {url}")
    resp = _session.get(url, params=params, headers=final_headers, timeout=timeout)
    resp.raise_for_status()
    return resp


def post(
    url: str,
    data: Optional[dict] = None,
    json: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: int = REQUEST_TIMEOUT,
    delay: bool = True,
) -> requests.Response:
    if delay:
        wait = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
        logger.debug(f"Rate limit: sleeping {wait:.1f}s before request")
        time.sleep(wait)

    final_headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/html, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    if headers:
        final_headers.update(headers)

    logger.info(f"POST {url}")
    resp = _session.post(url, data=data, json=json, headers=final_headers, timeout=timeout)
    resp.raise_for_status()
    return resp
