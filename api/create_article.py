import json
from typing import Any, Dict

import requests

from api.cookie_local import load_cookie_local


def api_create_article(title: str, content: str) -> Dict[str, Any]:
	"""创建文章（只封装标题与内容两个入参）。

	注意：params 中的 hkey/_time/nonce 通常来自抓包，可能会过期；
	若接口返回鉴权/非法请求相关错误，可更新下面的常量。
	"""

	url = "https://api.xiaoheihe.cn/wiki/create_article/"
	params = {
		"app": "heybox",
		"heybox_id": "",
		"os_type": "web",
		"x_app": "heybox_website",
		"x_client_type": "weboutapp",
		"x_os_type": "Windows",
		"version": "999.0.4",
		"hkey": "2Z3IT19",
		"_time": "1767669639",
		"nonce": "BB9716F7F0A123D8B959CED607DB79B9",
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

	data = {
		"article_type": "1",
		"game_id": "238960",                                                                    
		"name": title,
		"reference": '[{"category_id":17775174,"category_name":"通货"}]',
		"text": content,
	}

	resp = requests.post(
		url,
		params=params,
		data=data,
		headers=headers,
		timeout=15,
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
	# 避免误触发创建：这里只做导入/格式化演示，不主动发请求。
	t = api_create_article("示例标题", "示例内容")
	print(t)
