#!/usr/bin/env python3
"""
檔案連結蒐集工具
走訪指定網站的所有網頁，蒐集特定副檔名的檔案連結，輸出完整 URL 列表
用法: python getPage.py <起始URL> [--ext .pdf .zip ...] [--output 輸出檔名]
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import argparse
from pathlib import Path


class FileLinkCollector:
    def __init__(self, base_url, target_exts=None):
        self.base_url = base_url.rstrip('/')
        self.base_domain = urlparse(base_url).netloc
        self.target_exts = [e.lower() if e.startswith('.') else f'.{e.lower()}'
                            for e in (target_exts or ['.pdf'])]
        self.visited_pages = set()
        self.found_files = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_page(self, url):
        """取得網頁 HTML 內容"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except Exception as e:
            print(f"  [略過] 無法取得 {url}: {e}")
            return None

    def is_same_domain(self, url):
        """判斷是否屬於相同網域"""
        return urlparse(url).netloc == self.base_domain

    def extract_links(self, html, current_url):
        """從頁面中提取所有連結，分為可繼續走訪的頁面與目標檔案"""
        soup = BeautifulSoup(html, 'html.parser')
        page_links = set()
        file_links = set()

        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            if not href or href.startswith('#') or href.startswith('mailto:'):
                continue

            abs_url = urljoin(current_url, href)
            parsed = urlparse(abs_url)

            # 只處理 http/https
            if parsed.scheme not in ('http', 'https'):
                continue

            path_lower = parsed.path.lower()

            # 目標副檔名 → 收入檔案清單
            if any(path_lower.endswith(ext) for ext in self.target_exts):
                # 去除 fragment，保留完整 URL
                clean_url = abs_url.split('#')[0]
                file_links.add(clean_url)
            # 同網域的 HTML 頁面 → 繼續走訪
            elif self.is_same_domain(abs_url):
                # 排除已知靜態資源副檔名
                skip_exts = ('.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
                             '.css', '.js', '.woff', '.woff2', '.ttf', '.mp4')
                if not any(path_lower.endswith(e) for e in skip_exts):
                    page_links.add(abs_url.split('#')[0])

        return page_links, file_links

    def crawl(self, start_url):
        """開始走訪並蒐集目標檔案連結"""
        urls_to_visit = {start_url}
        found_file_urls = set()

        print(f"起始網址: {start_url}")
        print(f"目標副檔名: {', '.join(self.target_exts)}")
        print("-" * 60)

        while urls_to_visit:
            url = urls_to_visit.pop()

            if url in self.visited_pages:
                continue

            self.visited_pages.add(url)
            print(f"[{len(self.visited_pages):>4}] 走訪: {url}")

            html = self.get_page(url)
            if not html:
                continue

            page_links, file_links = self.extract_links(html, url)

            # 新發現的目標檔案
            new_files = file_links - found_file_urls
            if new_files:
                for f in sorted(new_files):
                    print(f"       ★ 找到: {f}")
                found_file_urls.update(new_files)

            # 新的頁面加入待訪佇列
            urls_to_visit.update(page_links - self.visited_pages)

            time.sleep(0.3)

        print("-" * 60)
        print(f"走訪完成，共 {len(self.visited_pages)} 個頁面，找到 {len(found_file_urls)} 個目標檔案")
        return sorted(found_file_urls)

    def save(self, file_urls, output_path):
        """將 URL 列表寫入文字檔"""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, 'w', encoding='utf-8') as f:
            for url in file_urls:
                f.write(url + '\n')
        print(f"已儲存 URL 列表: {output}  ({len(file_urls)} 筆)")


def main():
    parser = argparse.ArgumentParser(
        description='走訪網站並蒐集特定副檔名的檔案連結，輸出為 URL 列表'
    )
    parser.add_argument('url', help='起始網址')
    parser.add_argument(
        '--ext', nargs='+', default=['.pdf'], metavar='副檔名',
        help='要蒐集的副檔名，可多個，例如: --ext .pdf .zip .docx  (預設: .pdf)'
    )
    parser.add_argument(
        '--output', default='URL列表.txt', metavar='輸出檔名',
        help='輸出的文字檔路徑  (預設: URL列表.txt)'
    )
    args = parser.parse_args()

    collector = FileLinkCollector(args.url, target_exts=args.ext)
    file_urls = collector.crawl(args.url)

    if file_urls:
        collector.save(file_urls, args.output)
    else:
        print("未找到任何目標檔案連結。")


if __name__ == "__main__":
    main()
