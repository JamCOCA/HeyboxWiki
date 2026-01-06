import json
from typing import Any, Dict

import requests

from cookie_local import load_cookie_local


def api_create_template(name: str,css : str, content: str) -> Dict[str, Any]:
	"""创建模板（只封装两个入参：name + content）。

	注意：params 中的 hkey/_time/nonce 通常来自抓包，可能会过期；
	若接口返回鉴权/非法请求相关错误，可更新下面的常量。
	"""

	url = "https://api.xiaoheihe.cn/wiki/create_template/"
	params = {
		"app": "heybox",
		"heybox_id": "19636525",
		"os_type": "web",
		"x_app": "heybox_website",
		"x_client_type": "weboutapp",
		"x_os_type": "Windows",
		"version": "999.0.4",
		"hkey": "PU03715",
		"_time": "1767679018",
		"nonce": "24FAF26163E4E90174CAD2A5943F0C8C",
		"template_type": "user",
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

	# 由于你还没贴 Form Data，这里先按与 create_article 同风格的字段命名：name/text。
	# 如果你抓包的字段不同（例如 template_name/template_content），把下面两个 key 改掉即可。
	data = {
		"name": name,
		"text": content,
		"css":css
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
    t = api_create_template("示例模板","body {background-color: #f0f0f0;}","示例内容")
    print(t)
