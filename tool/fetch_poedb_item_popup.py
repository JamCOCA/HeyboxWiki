from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import re
from pathlib import Path
from datetime import datetime


URL = "https://poedb.tw/cn/Blacksmiths_Whetstone"


def _extract_lines_and_image(html: str) -> tuple[list[str], str]:
	try:
		from bs4 import BeautifulSoup  # type: ignore[import-not-found]
	except ImportError as e:
		raise ImportError("缺少依赖 beautifulsoup4，请先安装 requirements.txt") from e

	soup = BeautifulSoup(html, "html.parser")

	popup = soup.select_one("div.newItemPopup.currencyPopup") or soup.select_one("div.newItemPopup")
	if popup is None:
		raise ValueError("未找到 .newItemPopup，可能页面结构变更或尚未渲染完成")

	# 同组图片一般位于 popup 的祖先容器中
	image_src = ""
	container = popup
	for _ in range(6):
		img = container.select_one("div.itemboximage img")
		if img and img.get("src"):
			image_src = str(img.get("src"))
			break
		if container.parent is None:
			break
		container = container.parent

	# 逐行抽取：按页面展示顺序把关键块的文本拆成行
	lines: list[str] = []

	name = popup.select_one(".itemName .lc")
	if name:
		lines.append(name.get_text(strip=True))

	for prop in popup.select(".Stats .property"):
		text = prop.get_text(" ", strip=True)
		if not text:
			continue
		# 货币类弹窗里偶尔会出现“限制: 1”等属性，这会导致返回列表下标整体后移。
		# 下游逻辑按固定位置取值，因此这里过滤掉该行。
		# 过滤不稳定/不需要的属性行：例如“限制: 1”（不同物品可能是其他数字）
		if re.match(r"^限制\s*:?\s*\d+\s*$", text):
			continue
		# 例：堆叠数量: 1/40（或 1 / 40） -> 拆成两项：
		# - 堆叠数量
		# - 1/40
		m = re.match(r"^(堆叠数量)\s*:?\s*(\d+)\s*/\s*(\d+)$", text)
		if m:
			lines.append(m.group(1))
			lines.append(f"{m.group(2)}/{m.group(3)}")
			continue
		lines.append(text)

	for mod in popup.select(".Stats .explicitMod"):
		text = mod.get_text(" ", strip=True)
		if text:
			lines.append(text)

	default_desc = popup.select_one(".default")
	if default_desc:
		# 保留换行（你示例里需要把 Shift 那行保留下来）
		text = default_desc.get_text("\n", strip=True)
		if text:
			lines.append(text)

	# 英文名（示例中在 content 下的最后一个 div）
	content = popup.select_one(".content")
	if content:
		divs = content.find_all("div", recursive=False)
		if divs:
			text = divs[-1].get_text(" ", strip=True)
			if text:
				lines.append(text)

	return lines, image_src


def fetch_poedb_item_lines(url: str, *, timeout_ms: int = 60000, headless: bool = True) -> list[str]:
	"""抓取 POEDB 页面，返回内容文本 list（最后一项为图片链接，如果能找到）。"""
	with sync_playwright() as p:
		browser = p.chromium.launch(headless=headless)
		page = browser.new_page(locale="zh-CN")
		page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
		# POEDB 的弹窗内容通常依赖 JS/资源加载，domcontentloaded 后未必已经渲染完成。
		page.wait_for_load_state("networkidle", timeout=timeout_ms)
		try:
			page.wait_for_selector("div.newItemPopup", timeout=timeout_ms, state="attached")
		except PlaywrightTimeoutError as e:
			# 便于排查：把当时页面快照落地到 tmp/
			tmp_dir = Path(__file__).resolve().parents[1] / "tmp"
			tmp_dir.mkdir(parents=True, exist_ok=True)
			tag = datetime.now().strftime("%Y%m%d_%H%M%S")
			safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", url)[:80]
			screenshot_path = tmp_dir / f"poedb_timeout_{tag}_{safe_name}.png"
			html_path = tmp_dir / f"poedb_timeout_{tag}_{safe_name}.html"
			try:
				page.screenshot(path=str(screenshot_path), full_page=True)
			except Exception:
				pass
			try:
				html_path.write_text(page.content(), encoding="utf-8")
			except Exception:
				pass
			browser.close()
			raise PlaywrightTimeoutError(
				f"等待 div.newItemPopup 超时（{timeout_ms}ms）。已保存截图/HTML 到 tmp/："
				f"{screenshot_path.name} / {html_path.name}"
			) from e
		html = page.content()
		browser.close()

	lines, image_src = _extract_lines_and_image(html)
	if image_src:
		lines.append(image_src)
	return lines


if __name__ == "__main__":
    t = fetch_poedb_item_lines("https://poedb.tw/cn/Scroll_of_Wisdom")
    print(t)
