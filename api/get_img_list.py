import json
from typing import Any, Dict, Optional

import requests

from api.cookie_local import load_cookie_local


def api_get_img_list(
	offset: int = 0,
	limit: int = 10,
	timeout: float = 15,
) -> Dict[str, Any]:
	"""获取图片列表。

	对应抓包：
	- https://api.xiaoheihe.cn/wiki/get_img_list/

	说明：
	- hkey/_time/nonce 通常来自抓包，可能会过期；如遇“非法请求/鉴权失败”，更新下方常量。
	- offset/limit 用于分页。
	"""

	# 抓包固定参数（需要更新时改这里即可）
	wiki_id = "238960"
	hkey = "I3U1P35"
	_time = "1767685034"
	nonce = "A62B142F06F2100B3D774459CFBFE0BC"

	url = "https://api.xiaoheihe.cn/wiki/get_img_list/"
	params: Dict[str, str] = {
		"app": "heybox",
		"heybox_id": "",
		"os_type": "web",
		"x_app": "heybox_website",
		"x_client_type": "weboutapp",
		"x_os_type": "Windows",
		"version": "999.0.4",
		"hkey": hkey,
		"_time": _time,
		"nonce": nonce,
		"wiki_id": str(wiki_id),
		"offset": str(offset),
		"limit": str(limit),
	}

	# 参照现有实现：不声明 zstd，避免 requests 无法自动解压导致 resp.json() 失败。
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

	cookie_header: Optional[str] = load_cookie_local()
	if cookie_header:
		headers["Cookie"] = cookie_header

	resp = requests.post(
		url,
		params=params,
		data="",
		headers=headers,
		timeout=timeout,
	)
	resp.raise_for_status()
	return resp.json()


if __name__ == "__main__":
	# 简单运行示例：打印前 2000 字符，避免控制台刷屏
	try:
		data = api_get_img_list(offset=0, limit=10)
		print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
	except requests.HTTPError as e:
		resp = getattr(e, "response", None)
		if resp is not None:
			print("HTTP 状态码:", resp.status_code)
			print(resp.text[:2000])
		raise
