#!/usr/bin/env python3
"""
Notion API ドキュメントダウンローダー
ObsidianディレクトリにNotionドキュメントを保存するツール
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
import argparse
from typing import Dict, List, Optional

class NotionDownloader:
    def __init__(self, token: str, base_path: str = "."):
        """
        NotionDownloaderの初期化
        
        Args:
            token (str): Notion API トークン
            base_path (str): 保存先のベースパス（デフォルト: カレントディレクトリ）
        """
        self.token = token
        self.base_path = Path(base_path)
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
    def get_page_content(self, page_id: str) -> Dict:
        """
        ページの内容を取得
        
        Args:
            page_id (str): NotionページID
            
        Returns:
            Dict: ページの内容
        """
        url = f"https://api.notion.com/v1/pages/{page_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_block_children(self, block_id: str) -> List[Dict]:
        """
        ブロックの子要素を取得
        
        Args:
            block_id (str): ブロックID
            
        Returns:
            List[Dict]: 子ブロックのリスト
        """
        url = f"https://api.notion.com/v1/blocks/{block_id}/children"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["results"]
    
    def search_pages(self, query: str = "") -> List[Dict]:
        """
        ページを検索
        
        Args:
            query (str): 検索クエリ
            
        Returns:
            List[Dict]: 検索結果のページリスト
        """
        url = "https://api.notion.com/v1/search"
        data = {
            "query": query,
            "filter": {
                "property": "object",
                "value": "page"
            }
        }
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()["results"]
    
    def block_to_markdown(self, block: Dict) -> str:
        """
        ブロックをMarkdownに変換
        
        Args:
            block (Dict): Notionブロック
            
        Returns:
            str: Markdown形式のテキスト
        """
        block_type = block["type"]
        content = block[block_type]
        
        if block_type == "paragraph":
            text = self._extract_text(content.get("rich_text", []))
            return f"{text}\n\n"
        
        elif block_type == "heading_1":
            text = self._extract_text(content.get("rich_text", []))
            return f"# {text}\n\n"
        
        elif block_type == "heading_2":
            text = self._extract_text(content.get("rich_text", []))
            return f"## {text}\n\n"
        
        elif block_type == "heading_3":
            text = self._extract_text(content.get("rich_text", []))
            return f"### {text}\n\n"
        
        elif block_type == "bulleted_list_item":
            text = self._extract_text(content.get("rich_text", []))
            return f"- {text}\n"
        
        elif block_type == "numbered_list_item":
            text = self._extract_text(content.get("rich_text", []))
            return f"1. {text}\n"
        
        elif block_type == "to_do":
            text = self._extract_text(content.get("rich_text", []))
            checked = content.get("checked", False)
            checkbox = "[x]" if checked else "[ ]"
            return f"{checkbox} {text}\n"
        
        elif block_type == "code":
            text = self._extract_text(content.get("rich_text", []))
            language = content.get("language", "")
            return f"```{language}\n{text}\n```\n\n"
        
        elif block_type == "quote":
            text = self._extract_text(content.get("rich_text", []))
            return f"> {text}\n\n"
        
        elif block_type == "callout":
            text = self._extract_text(content.get("rich_text", []))
            icon = content.get("icon", {}).get("emoji", "💡")
            return f"{icon} {text}\n\n"
        
        elif block_type == "divider":
            return "---\n\n"
        
        elif block_type == "image":
            image_url = content.get("external", {}).get("url") or content.get("file", {}).get("url")
            caption = self._extract_text(content.get("caption", []))
            caption_text = f" {caption}" if caption else ""
            return f"![{caption}]({image_url}){caption_text}\n\n"
        
        elif block_type == "table_of_contents":
            return "[[目次]]\n\n"
        
        else:
            # 未対応のブロックタイプ
            return f"<!-- 未対応ブロック: {block_type} -->\n\n"
    
    def _extract_text(self, rich_text: List[Dict]) -> str:
        """
       リッチテキストからプレーンテキストを抽出
        
        Args:
            rich_text (List[Dict]): リッチテキストのリスト
            
        Returns:
            str: プレーンテキスト
        """
        text_parts = []
        for text_block in rich_text:
            if text_block.get("type") == "text":
                text_content = text_block["text"]["content"]
                annotations = text_block.get("annotations", {})
                
                # アノテーションを適用
                if annotations.get("bold"):
                    text_content = f"**{text_content}**"
                if annotations.get("italic"):
                    text_content = f"*{text_content}*"
                if annotations.get("strikethrough"):
                    text_content = f"~~{text_content}~~"
                if annotations.get("code"):
                    text_content = f"`{text_content}`"
                
                # リンクを処理
                if text_block["text"].get("link"):
                    link_url = text_block["text"]["link"]["url"]
                    text_content = f"[{text_content}]({link_url})"
                
                text_parts.append(text_content)
        
        return "".join(text_parts)
    
    def get_page_title(self, page: Dict) -> str:
        """
        ページのタイトルを取得
        
        Args:
            page (Dict): ページデータ
            
        Returns:
            str: ページタイトル
        """
        properties = page.get("properties", {})
        
        # タイトルプロパティを探す
        for prop_name, prop_value in properties.items():
            if prop_value.get("type") == "title":
                title_blocks = prop_value["title"]
                if title_blocks:
                    return self._extract_text(title_blocks)
        
        # タイトルが見つからない場合はページIDを使用
        return f"Untitled-{page['id'][:8]}"
    
    def download_page(self, page_id: str, output_dir: Optional[str] = None) -> str:
        """
        ページをダウンロードしてMarkdownファイルとして保存
        
        Args:
            page_id (str): NotionページID
            output_dir (Optional[str]): 出力ディレクトリ（デフォルト: base_path）
            
        Returns:
            str: 保存されたファイルのパス
        """
        print(f"ページをダウンロード中: {page_id}")
        
        # ページ情報を取得
        page = self.get_page_content(page_id)
        title = self.get_page_title(page)
        
        # ファイル名を生成（安全なファイル名に変換）
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        filename = f"{safe_title}.md"
        
        # 出力ディレクトリを決定
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = self.base_path
        
        output_path.mkdir(parents=True, exist_ok=True)
        file_path = output_path / filename
        
        # ページの内容を取得
        blocks = self.get_block_children(page_id)
        
        # Markdownに変換
        markdown_content = []
        
        # メタデータを追加
        markdown_content.append(f"# {title}\n")
        markdown_content.append(f"**作成日**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        markdown_content.append(f"**NotionページID**: {page_id}\n")
        markdown_content.append(f"**URL**: https://notion.so/{page_id.replace('-', '')}\n\n")
        markdown_content.append("---\n\n")
        
        # ブロックを処理
        for block in blocks:
            markdown_content.append(self.block_to_markdown(block))
            
            # 子ブロックがある場合は再帰的に処理
            if block.get("has_children", False):
                child_blocks = self.get_block_children(block["id"])
                for child_block in child_blocks:
                    markdown_content.append(self.block_to_markdown(child_block))
        
        # ファイルに保存
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(''.join(markdown_content))
        
        print(f"ファイルを保存しました: {file_path}")
        return str(file_path)
    
    def download_database(self, database_id: str, output_dir: Optional[str] = None) -> List[str]:
        """
        データベースの全ページをダウンロード
        
        Args:
            database_id (str): NotionデータベースID
            output_dir (Optional[str]): 出力ディレクトリ
            
        Returns:
            List[str]: 保存されたファイルのパスリスト
        """
        print(f"データベースをダウンロード中: {database_id}")
        
        # データベースのページを取得
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        response = requests.post(url, headers=self.headers, json={})
        response.raise_for_status()
        
        pages = response.json()["results"]
        saved_files = []
        
        for page in pages:
            page_id = page["id"]
            try:
                file_path = self.download_page(page_id, output_dir)
                saved_files.append(file_path)
            except Exception as e:
                print(f"ページ {page_id} のダウンロードに失敗: {e}")
        
        return saved_files

def main():
    parser = argparse.ArgumentParser(description="Notion API ドキュメントダウンローダー")
    parser.add_argument("--token", required=True, help="Notion API トークン")
    parser.add_argument("--page-id", help="ダウンロードするページID")
    parser.add_argument("--database-id", help="ダウンロードするデータベースID")
    parser.add_argument("--search", help="検索クエリ")
    parser.add_argument("--output-dir", default=".", help="出力ディレクトリ")
    parser.add_argument("--list-pages", action="store_true", help="利用可能なページを一覧表示")
    
    args = parser.parse_args()
    
    downloader = NotionDownloader(args.token, args.output_dir)
    
    if args.list_pages:
        print("利用可能なページを検索中...")
        pages = downloader.search_pages(args.search or "")
        print(f"\n見つかったページ数: {len(pages)}")
        for i, page in enumerate(pages, 1):
            title = downloader.get_page_title(page)
            page_id = page["id"]
            print(f"{i}. {title} (ID: {page_id})")
    
    elif args.page_id:
        try:
            file_path = downloader.download_page(args.page_id, args.output_dir)
            print(f"ダウンロード完了: {file_path}")
        except Exception as e:
            print(f"エラー: {e}")
    
    elif args.database_id:
        try:
            file_paths = downloader.download_database(args.database_id, args.output_dir)
            print(f"ダウンロード完了: {len(file_paths)} ファイル")
            for file_path in file_paths:
                print(f"  - {file_path}")
        except Exception as e:
            print(f"エラー: {e}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 