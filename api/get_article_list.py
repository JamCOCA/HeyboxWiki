import json
from typing import Any, Dict

import requests

from cookie_local import load_cookie_local


def api_get_article_list(
    timeout: float = 15,
) -> Dict[str, Any]:
    """最简单的接口测试封装：请求 heybox wiki/get_article_list。

    说明：
    - 这里使用 requests（你已经安装了）
    - 按你提供的 URL，把所有 query 参数都加进来
    - 返回 JSON（如果服务端不是 JSON，会抛异常）
    """

    url = "https://api.xiaoheihe.cn/wiki/get_article_list/"
    params = {
        "app": "heybox",
        "heybox_id": "",
        "os_type": "web",
        "x_app": "heybox_website",
        "x_client_type": "weboutapp",
        "x_os_type": "Windows",
        "version": "999.0.4",
        "hkey": "IV3TV72",
        "_time": "1766738736",
        "nonce": "9F295E7B02CE993009DC1F8B66883FDB",
        "wiki_id": "238960",
        "offset": "0",
        "limit": "10",
    }

    # 按你抓包的请求头尽量补全
    # 注意：不要声明 zstd（requests 默认不支持解 zstd），否则服务端可能返回 zstd 导致这边解析失败。
    headers: Dict[str, str] = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Origin": "https://c.xiaoheihe.cn",
        "Referer": "https://c.xiaoheihe.cn/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    }

    # Cookie：从本地文件读取并放入请求头（如果没有就不带 Cookie）
    cookie_header = load_cookie_local()
    if cookie_header:
        headers["Cookie"] = cookie_header
    

    resp = requests.post(
        url,
        params=params,
        data="",
        headers=headers,
        timeout=timeout,
    )
    # 非 2xx 直接抛错，方便你测试时快速发现问题
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    # 简单运行示例：打印前 2000 字符，避免控制台刷屏
    try:
        data = api_get_article_list()
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
    except requests.HTTPError as e:
        # HTTP 状态码异常时，把响应体也打出来，方便判断是否“非法请求/鉴权失败”
        resp = getattr(e, "response", None)
        if resp is not None:
            print("HTTP 状态码:", resp.status_code)
            print(resp.text[:2000])
        raise