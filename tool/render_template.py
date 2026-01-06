from __future__ import annotations

import os
from pathlib import Path
from string import Template



def render_item_popup(
    template_path: str | os.PathLike[str],
    *,
    title: str,
    category: str,
    stack: str,
    affix: str,
    desc_html: str,
    en: str,
    icon_url: str,
    out_path: str | os.PathLike[str],
) -> str:
    """从模板加载 `item_popup.html`，用必填参数填充占位符，并保存为 HTML 文件。

    必填参数（对应模板占位符）：
        - title, category, stack, affix, desc_html, en, icon_url

    返回：输出文件路径（str）。
    """

    tmpl_path = Path(template_path)
    if not tmpl_path.exists():
        raise FileNotFoundError(tmpl_path)

    text = tmpl_path.read_text(encoding="utf-8")

    # 这些字段全部必传；这里统一转成 str，避免传入 None/数字时报错
    safe = {
        "title": str(title),
        "category": str(category),
        "stack": str(stack),
        "affix": str(affix),
        "desc_html": str(desc_html),
        "en": str(en),
        "icon_url": str(icon_url),
    }

    # icon_url 优先使用传入的 icon_url，否则保留模板里的 img src（模板内已设置默认）
    # 我们用 Template.safe_substitute 以避免未传入 key 抛错
    t = Template(text)
    rendered = t.safe_substitute(safe)

    outp = Path(out_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(rendered, encoding="utf-8")
    return str(outp)


if __name__ == "__main__":
    out = render_item_popup(
        Path("template") / "Item" / "item_popup.html",
        title="增幅植入体（示例）",
        category="通货",
        stack="1 / 10",
        affix="为魔法接枝物新增 1 条随机词缀",
        desc_html="右键点击此物品，再左键点击一个魔法接枝物来使用。<br>按住 SHIFT 点击以分开堆叠",
        en="AUGMENTATION IMPLANT",
        icon_url="https://cdn.max-c.com/wiki/238960/GraftedAugmentation.png?v=1",
        out_path=Path("tmp") / "rendered_item_popup.html",
    )
    print("wrote", out)
