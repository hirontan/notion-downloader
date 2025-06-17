#!/usr/bin/env python3
"""
Notionダウンローダーヘルパー
設定ファイルを使用してNotionドキュメントをダウンロードする便利なスクリプト
"""

import json
import os
import sys
import re
from pathlib import Path
from notion_downloader import NotionDownloader

# .envファイルを自動的に読み込み
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenvがインストールされていない場合は無視
    pass

def resolve_environment_variables(value):
    """
    文字列内の環境変数を解決する
    
    Args:
        value: 解決対象の値
        
    Returns:
        環境変数が解決された値
    """
    if isinstance(value, str):
        # ${ENV_VAR} 形式の環境変数を解決
        pattern = r'\$\{([^}]+)\}'
        def replace_env_var(match):
            env_var = match.group(1)
            return os.getenv(env_var, match.group(0))
        
        return re.sub(pattern, replace_env_var, value)
    return value

def resolve_config_values(config):
    """
    設定辞書内のすべての値を再帰的に解決する
    
    Args:
        config: 設定辞書
        
    Returns:
        環境変数が解決された設定辞書
    """
    if isinstance(config, dict):
        return {key: resolve_config_values(value) for key, value in config.items()}
    elif isinstance(config, list):
        return [resolve_config_values(item) for item in config]
    else:
        return resolve_environment_variables(config)

def load_config(config_path: str = "notion_config.json") -> dict:
    """
    設定ファイルを読み込み、環境変数を解決
    
    Args:
        config_path (str): 設定ファイルのパス
        
    Returns:
        dict: 設定データ
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 環境変数を解決
        config = resolve_config_values(config)
        
        return config
    except FileNotFoundError:
        print(f"設定ファイルが見つかりません: {config_path}")
        print("notion_config.jsonを作成してください")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"設定ファイルの形式が正しくありません: {e}")
        sys.exit(1)

def setup_notion_integration():
    """
    Notion統合のセットアップ手順を表示
    """
    print("=== Notion統合のセットアップ ===")
    print("1. https://www.notion.so/my-integrations にアクセス")
    print("2. 「New integration」をクリック")
    print("3. 統合の名前を入力（例: Obsidian Sync）")
    print("4. Submit をクリック")
    print("5. Internal Integration Token をコピー")
    print("6. .env.sample から .env をコピー:")
    print("   cp .env.sample .env")
    print("7. .env ファイルをエディタで開き、NOTION_TOKENにトークンを設定:")
    print("   NOTION_TOKEN=your_token_here")
    print("8. ダウンロードしたいページで統合を追加")
    print("   - ページ右上の「...」→「Add connections」→統合を選択")
    print()

def download_single_page(page_id: str, config: dict):
    """
    単一ページをダウンロード
    
    Args:
        page_id (str): NotionページID
        config (dict): 設定データ
    """
    token = config["notion"]["token"]
    output_dir = config["notion"]["default_output_dir"]
    
    if not token or token == "${NOTION_TOKEN}":
        print("エラー: Notion API トークンが設定されていません")
        print("環境変数 NOTION_TOKEN を設定するか、notion_config.json で直接トークンを設定してください")
        setup_notion_integration()
        return
    
    downloader = NotionDownloader(token, output_dir)
    
    try:
        file_path = downloader.download_page(page_id, output_dir)
        print(f"✅ ダウンロード完了: {file_path}")
    except Exception as e:
        print(f"❌ エラー: {e}")

def download_database_pages(database_id: str, config: dict):
    """
    データベースの全ページをダウンロード
    
    Args:
        database_id (str): NotionデータベースID
        config (dict): 設定データ
    """
    token = config["notion"]["token"]
    output_dir = config["notion"]["default_output_dir"]
    
    if not token or token == "${NOTION_TOKEN}":
        print("エラー: Notion API トークンが設定されていません")
        print("環境変数 NOTION_TOKEN を設定するか、notion_config.json で直接トークンを設定してください")
        setup_notion_integration()
        return
    
    downloader = NotionDownloader(token, output_dir)
    
    try:
        file_paths = downloader.download_database(database_id, output_dir)
        print(f"✅ ダウンロード完了: {len(file_paths)} ファイル")
        for file_path in file_paths:
            print(f"  📄 {file_path}")
    except Exception as e:
        print(f"❌ エラー: {e}")

def search_and_download(query: str, config: dict):
    """
    検索してページをダウンロード
    
    Args:
        query (str): 検索クエリ
        config (dict): 設定データ
    """
    token = config["notion"]["token"]
    output_dir = config["notion"]["default_output_dir"]
    
    if not token or token == "${NOTION_TOKEN}":
        print("エラー: Notion API トークンが設定されていません")
        print("環境変数 NOTION_TOKEN を設定するか、notion_config.json で直接トークンを設定してください")
        setup_notion_integration()
        return
    
    downloader = NotionDownloader(token, output_dir)
    
    try:
        pages = downloader.search_pages(query)
        print(f"🔍 検索結果: {len(pages)} ページ")
        
        if not pages:
            print("ページが見つかりませんでした")
            return
        
        for i, page in enumerate(pages, 1):
            title = downloader.get_page_title(page)
            page_id = page["id"]
            print(f"{i}. {title}")
        
        choice = input("\nダウンロードするページ番号を入力（複数の場合はカンマ区切り、すべての場合は 'all'）: ")
        
        if choice.lower() == 'all':
            selected_pages = pages
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                selected_pages = [pages[i] for i in indices if 0 <= i < len(pages)]
            except (ValueError, IndexError):
                print("無効な選択です")
                return
        
        for page in selected_pages:
            page_id = page["id"]
            title = downloader.get_page_title(page)
            print(f"\n📥 {title} をダウンロード中...")
            try:
                file_path = downloader.download_page(page_id, output_dir)
                print(f"✅ 完了: {file_path}")
            except Exception as e:
                print(f"❌ エラー: {e}")
                
    except Exception as e:
        print(f"❌ エラー: {e}")

def show_database_info(database_id: str, config: dict):
    """
    データベースの情報を表示
    
    Args:
        database_id (str): NotionデータベースID
        config (dict): 設定データ
    """
    token = config["notion"]["token"]
    
    if not token or token == "${NOTION_TOKEN}":
        print("エラー: Notion API トークンが設定されていません")
        print("環境変数 NOTION_TOKEN を設定するか、notion_config.json で直接トークンを設定してください")
        setup_notion_integration()
        return
    
    downloader = NotionDownloader(token)
    
    try:
        print(f"📊 データベース情報を取得中: {database_id}")
        
        # データベースの基本情報を取得
        database_info = downloader.get_database_info(database_id)
        title = downloader.get_page_title(database_info)
        
        print(f"\n📋 データベース名: {title}")
        print(f"🆔 データベースID: {database_id}")
        print(f"📅 作成日: {database_info.get('created_time', 'N/A')}")
        print(f"🔄 最終更新: {database_info.get('last_edited_time', 'N/A')}")
        
        # スキーマ（プロパティ）を表示
        properties = database_info.get("properties", {})
        print(f"\n🏗️  プロパティ ({len(properties)}個):")
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get("type", "unknown")
            print(f"  • {prop_name} ({prop_type})")
        
        # ページリストを取得
        pages = downloader.get_database_pages(database_id)
        print(f"\n📄 ページ ({len(pages)}個):")
        
        if not pages:
            print("  データベースにページがありません")
        else:
            for i, page in enumerate(pages, 1):
                page_title = downloader.get_page_title(page)
                page_id = page["id"]
                created_time = page.get("created_time", "N/A")
                print(f"  {i}. {page_title}")
                print(f"     ID: {page_id}")
                print(f"     作成日: {created_time}")
                
                # プロパティの値を表示
                page_properties = page.get("properties", {})
                for prop_name, prop_value in page_properties.items():
                    if prop_value.get("type") in ["title", "rich_text", "select", "multi_select", "date"]:
                        prop_content = prop_value.get(prop_value["type"], [])
                        if isinstance(prop_content, list) and prop_content:
                            if prop_value["type"] == "title":
                                text = downloader._extract_text(prop_content)
                            elif prop_value["type"] == "rich_text":
                                text = downloader._extract_text(prop_content)
                            elif prop_value["type"] == "select":
                                text = prop_content.get("name", "")
                            elif prop_value["type"] == "multi_select":
                                text = ", ".join([item.get("name", "") for item in prop_content])
                            elif prop_value["type"] == "date":
                                date_info = prop_content.get("start", "")
                                if prop_content.get("end"):
                                    date_info += f" - {prop_content['end']}"
                                text = date_info
                            else:
                                text = str(prop_content)
                            
                            if text:
                                print(f"     {prop_name}: {text}")
                print()
        
    except Exception as e:
        print(f"❌ エラー: {e}")

def download_database_as_table(database_id: str, config: dict):
    """
    データベースをマークダウンテーブル形式でダウンロード
    
    Args:
        database_id (str): NotionデータベースID
        config (dict): 設定データ
    """
    token = config["notion"]["token"]
    output_dir = config["notion"]["default_output_dir"]
    
    if not token or token == "${NOTION_TOKEN}":
        print("エラー: Notion API トークンが設定されていません")
        print("環境変数 NOTION_TOKEN を設定するか、notion_config.json で直接トークンを設定してください")
        setup_notion_integration()
        return
    
    downloader = NotionDownloader(token, output_dir)
    
    try:
        file_path = downloader.download_database_as_markdown_table(database_id, output_dir)
        print(f"✅ マークダウンテーブルダウンロード完了: {file_path}")
    except Exception as e:
        print(f"❌ エラー: {e}")

def main():
    """
    メイン関数
    """
    if len(sys.argv) < 2:
        print("=== Notionダウンローダーヘルパー ===")
        print("使用方法:")
        print("  python notion_helper.py page <page_id>")
        print("  python notion_helper.py database <database_id>")
        print("  python notion_helper.py download_table <database_id>")
        print("  python notion_helper.py search <query>")
        print("  python notion_helper.py info <database_id>")
        print("  python notion_helper.py setup")
        print()
        print("例:")
        print("  python notion_helper.py page 12345678-1234-1234-1234-123456789abc")
        print("  python notion_helper.py search プロジェクト計画")
        print("  python notion_helper.py info 87654321-4321-4321-4321-987654321cba")
        print("  python notion_helper.py download_table 87654321-4321-4321-4321-987654321cba")
        return
    
    config = load_config()
    
    command = sys.argv[1]
    
    if command == "setup":
        setup_notion_integration()
    
    elif command == "page" and len(sys.argv) >= 3:
        page_id = sys.argv[2]
        download_single_page(page_id, config)
    
    elif command == "database" and len(sys.argv) >= 3:
        database_id = sys.argv[2]
        download_database_pages(database_id, config)
    
    elif command == "download_table" and len(sys.argv) >= 3:
        database_id = sys.argv[2]
        download_database_as_table(database_id, config)
    
    elif command == "search" and len(sys.argv) >= 3:
        query = sys.argv[2]
        search_and_download(query, config)
    
    elif command == "info" and len(sys.argv) >= 3:
        database_id = sys.argv[2]
        show_database_info(database_id, config)
    
    else:
        print("無効なコマンドです")
        print("python notion_helper.py でヘルプを表示")

if __name__ == "__main__":
    main() 