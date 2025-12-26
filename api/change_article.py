import json
from typing import Any, Dict, Mapping, Optional, Union

import requests

from cookie_local import load_cookie_local


JsonLike = Union[Dict[str, Any], list, str, int, float, bool, None]


def api_change_article(
    *,
    wiki_id: Union[str, int] = "238960",
    user_type: Union[str, int] = 0,
    heybox_id: str = "",
    hkey: str = "YV7VI78",
    _time: Union[str, int] = "1766741105",
    nonce: str = "60A9652F1B010DA7E2E9C9A08D636FF4",
    form: Optional[Mapping[str, Any]] = None,
    json_body: Optional[JsonLike] = None,
    extra_params: Optional[Mapping[str, Any]] = None,
    timeout: float = 15,
) -> Dict[str, Any]:
    """封装 https://api.xiaoheihe.cn/wiki/change_article/ 接口请求。

    说明：
    - 该接口的 query 参数（hkey/_time/nonce 等）通常来自抓包；本函数提供默认值以便快速对齐你给的 URL。
      如果返回“非法请求/签名错误/鉴权失败”，优先更新这三个参数为最新抓包值。
    - 正文支持两种方式二选一：
        1) `form`: 以 `application/x-www-form-urlencoded` 形式提交（最常见）
        2) `json_body`: 以 JSON 形式提交（如果服务端要求 JSON）
      同时传入时，优先使用 `json_body`。

    参数：
    - wiki_id/user_type：来自你提供的 URL
    - form/json_body：你要“修改文章”时实际提交的字段（如 article_id/title/content 等）

    返回：
    - 服务端 JSON 反序列化后的 dict
    """

    url = "https://api.xiaoheihe.cn/wiki/change_article/"

    params: Dict[str, Any] = {
        "app": "heybox",
        "heybox_id": heybox_id,
        "os_type": "web",
        "x_app": "heybox_website",
        "x_client_type": "weboutapp",
        "x_os_type": "Windows",
        "version": "999.0.4",
        "hkey": hkey,
        "_time": str(_time),
        "nonce": nonce,
        "wiki_id": str(wiki_id),
        "user_type": str(user_type),
    }
    if extra_params:
        params.update(dict(extra_params))

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

    cookie_header = load_cookie_local()
    if cookie_header:
        headers["Cookie"] = cookie_header

    request_kwargs: Dict[str, Any] = {
        "url": url,
        "params": params,
        "headers": headers,
        "timeout": timeout,
    }

    if json_body is not None:
        # 如果你确认服务端收 JSON，传 json_body 更稳（同时把 Content-Type 改成 JSON）
        request_kwargs["json"] = json_body
        headers["Content-Type"] = "application/json"
        resp = requests.post(**request_kwargs)
    else:
        # 默认用 form（若不传则发空 body，跟 get_article_list.py 一致）
        resp = requests.post(
            **request_kwargs,
            data=dict(form) if form is not None else "",
        )

    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    # 运行示例：你需要把 form/json_body 的字段替换成你抓包里真正提交的字段。
    # 下面只是“结构示例”，不保证字段正确。
    try:
        data = api_change_article(
            wiki_id="238960",
            user_type=0,
            # form={
            #     "article_id": "123456",
            #     "title": "新标题",
            #     "content": "新内容...",
            # },
            form={},
        )
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except requests.HTTPError as e:
        resp = getattr(e, "response", None)
        if resp is not None:
            print("HTTP 状态码:", resp.status_code)
            print(resp.text[:2000])
        raise
