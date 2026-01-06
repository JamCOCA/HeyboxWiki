import json
import os
from typing import Any
import re

import tool.fetch_poedb_item_popup
import tool.render_template

def json_to_list(json_path, encoding: str = "utf-8") -> list[Any]:
    """读取 JSON 列表文件。"""
    with open(json_path, "r", encoding=encoding) as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"文件 {json_path} 内容不是列表")
        return data
    

def convert_poedb_img(url: str) -> str:
    m = re.search(r"/([^/]+?)\.webp(?:\?.*)?$", url)
    if not m:
        raise ValueError(f"不是期望的 poedb webp 链接: {url}")
    name = m.group(1)
    return f"https://cdn.max-c.com/wiki/238960/{name}.png?v=1"

if __name__ == "__main__":
    temp_list = []
    # 读取poedb所有条目
    data = json_to_list("data/20260106poedb.json")
    for x in data:
        if x.get("desc") == "可堆叠通货":
            temp_list.append(x)
    _l = temp_list[:2]
    for item in _l:
        print(item)
        o = tool.fetch_poedb_item_popup.fetch_poedb_item_lines(f"https://poedb.tw/cn/{item['value']}")
        print(o)
        out = tool.render_template.render_item_popup(
            "template/Item/item_popup.html",
            title=f"{o[0]}",
            category=f"{o[1]}",
            stack=f"{o[3]}",
            affix=f"{o[4]}",
            desc_html=f"{o[5]}",
            en=f"{o[6]}",
            icon_url=convert_poedb_img(o[7]),
            out_path=f"tmp/{o[6]}.html",
        )
        print("wrote", out)

