import json
from typing import Any, Dict

import requests

from cookie_local import load_cookie_local


def api_get_template_list(
	template_type: str = "user",
	timeout: float = 15,
) -> Dict[str, Any]:
	"""获取模板列表。

	只做最薄的一层封装：
	- template_type: 默认 admin
	- 自动从 api/cookies.local.json 注入 Cookie
	"""

	url = "https://api.xiaoheihe.cn/wiki/get_template_list/"
	params = {
		"app": "heybox",
		"heybox_id": "",
		"os_type": "web",
		"x_app": "heybox_website",
		"x_client_type": "weboutapp",
		"x_os_type": "Windows",
		"version": "999.0.4",
		"hkey": "X1WZU78",
		"_time": "1767678718",
		"nonce": "92EA8CFB92C106575AB147C09B0EB20C",
		"template_type": template_type,
		"wiki_id": "238960",
	}

	headers: Dict[str, str] = {
		"Accept": "application/json, text/plain, */*",
		"Accept-Encoding": "gzip, deflate, br, zstd",
		"Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
		"Connection": "keep-alive",
		"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
		"Host": "api.xiaoheihe.cn",
		"Origin": "https://c.xiaoheihe.cn",
		"Priority": "u=0",
		"Referer": "https://c.xiaoheihe.cn/",
		"Sec-Fetch-Dest": "empty",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Site": "same-site",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
	}

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
	resp.raise_for_status()

	try:
		return resp.json()
	except ValueError:
		content_encoding = (resp.headers.get("Content-Encoding") or "").lower()
		raw = resp.content

		if "zstd" in content_encoding:
			try:
				import zstandard as zstd  # type: ignore
			except Exception as e:
				raise RuntimeError(
					"服务端返回了 zstd 压缩响应，但当前环境缺少解压依赖。请先安装：pip install zstandard"
				) from e
			dctx = zstd.ZstdDecompressor()
			decoded = dctx.decompress(raw)
			return json.loads(decoded.decode("utf-8"))

		if "br" in content_encoding:
			try:
				import brotli  # type: ignore
			except Exception as e:
				raise RuntimeError(
					"服务端返回了 br 压缩响应，但当前环境缺少解压依赖。请先安装：pip install brotli"
				) from e
			decoded = brotli.decompress(raw)
			return json.loads(decoded.decode("utf-8"))

		raise


if __name__ == "__main__":
	try:
		data = api_get_template_list()
		print(json.dumps(data, ensure_ascii=False, indent=2))
	except requests.HTTPError as e:
		resp = getattr(e, "response", None)
		if resp is not None:
			print("HTTP 状态码:", resp.status_code)
			print(resp.text[:2000])
		raise
