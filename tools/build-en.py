#!/usr/bin/env python3
"""从中文地址的页面生成英文地址 /en/ 的页面（她 11-04：分享卡片的标题要有英文）。

分享卡片（微信、iMessage、Reddit…）读的是网页里写死的 og 标签，不跑脚本、不看语言，
所以英文平台发 /en/：内容和根目录一模一样，只是打开默认英文、卡片是英文、相对路径往上一层。
改了 index.html / qa.html 以后跑一次再上传：python3 tools/build-en.py
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://foxpix.douzifox.com"

PAGES = {
    "index.html": dict(
        path="",
        title="FoxPix: screenshot organizer and private vault for iPhone",
        og_title="FoxPix: Take the private stuff out of your camera roll",
        og_desc="Sorts your screenshots, finds IDs, bank cards and logins in them, and locks them in a vault that opens with Face ID or your passcode. Recognition runs on your iPhone; screenshots are never uploaded.",
    ),
    "qa.html": dict(
        path="qa.html",
        title="Screenshots and photo privacy: common questions · FoxPix",
        og_title="Screenshots and photo privacy: common questions",
        og_desc="Are ID photos in your camera roll safe? How to organize and bulk delete screenshots, and where to keep passwords. Straight answers first.",
    ),
}


def sub(html, pattern, repl, name):
    out, n = re.subn(pattern, repl, html, count=1)
    assert n == 1, f"{name}: 没找到 {pattern}"
    return out


for name, p in PAGES.items():
    html = (ROOT / name).read_text(encoding="utf-8")
    en_url = f"{SITE}/en/{p['path']}"
    html = sub(html, r'<html lang="zh-Hans" data-lang="zh">', '<html lang="en" data-lang="en">', name)
    # 这个地址就是英文的：不看浏览器语言、也不看上次选的，下拉框照样能切
    html = sub(html, r"if \(lang !== 'zh' && lang !== 'en'\) \{", "lang = 'en'; if (false) {", name)
    html = sub(html, r"<title>.*?</title>", f"<title>{p['title']}</title>", name)
    html = sub(html, r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{en_url}">', name)
    html = sub(html, r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{p["og_title"]}">', name)
    html = sub(html, r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{p["og_desc"]}">', name)
    html = sub(html, r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{en_url}">', name)
    html = sub(html, r'<meta property="og:locale" content="[^"]*">', '<meta property="og:locale" content="en_US">', name)
    # 相对路径往上一层；qa.html 和首页 ./ 在 /en/ 里也有，不动
    html = re.sub(r'(src|href)="(assets/|privacy\.html)', r'\1="../\2', html)
    (ROOT / "en").mkdir(exist_ok=True)
    (ROOT / "en" / name).write_text(html, encoding="utf-8")
    print("en/" + name)
