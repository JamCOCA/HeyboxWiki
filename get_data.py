import json
from typing import Any


def json_to_list(json_path, encoding: str = "utf-8") -> list[Any]:
    """读取 JSON 列表文件。"""
    with open(json_path, "r", encoding=encoding) as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"文件 {json_path} 内容不是列表")
        return data

if __name__ == "__main__":
    data = json_to_list("data/20260106poedb.json")
    for x in data:
        if x.get("desc") == "可堆叠通货":
            print(x)