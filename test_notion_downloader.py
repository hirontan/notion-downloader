#!/usr/bin/env python3
"""
Notionダウンローダーのテストスクリプト
"""

import os
import sys
from pathlib import Path

# .envファイルを自動的に読み込み
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenvがインストールされていない場合は無視
    pass

def test_imports():
    """必要なモジュールのインポートテスト"""
    print("🔍 モジュールインポートテスト...")
    
    try:
        import requests
        print("✅ requests モジュール: OK")
    except ImportError:
        print("❌ requests モジュール: インストールが必要")
        print("   pip install requests")
        return False
    
    try:
        from notion_downloader import NotionDownloader
        print("✅ NotionDownloader クラス: OK")
    except ImportError as e:
        print(f"❌ NotionDownloader クラス: {e}")
        return False
    
    return True

def test_config_file():
    """設定ファイルのテスト"""
    print("\n🔍 設定ファイルテスト...")
    
    config_path = Path("notion_config.json")
    if not config_path.exists():
        print("❌ notion_config.json が見つかりません")
        return False
    
    try:
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if "notion" not in config:
            print("❌ 設定ファイルに 'notion' セクションがありません")
            return False
        
        if "token" not in config["notion"]:
            print("❌ 設定ファイルに 'token' が設定されていません")
            return False
        
        token = config["notion"]["token"]
        
        # 環境変数が設定されているかチェック
        if token == "${NOTION_TOKEN}":
            env_token = os.getenv("NOTION_TOKEN")
            if not env_token:
                print("⚠️  環境変数 NOTION_TOKEN が設定されていません")
                print("   以下のいずれかの方法でトークンを設定してください:")
                print("   A. 環境変数として設定:")
                print("      export NOTION_TOKEN='your_token_here'")
                print("   B. notion_config.json で直接設定:")
                print("      \"token\": \"your_token_here\"")
                return False
            else:
                print("✅ 環境変数 NOTION_TOKEN: OK")
                return True
        
        if token == "your_notion_integration_token_here":
            print("⚠️  トークンがデフォルト値のままです")
            print("   notion_config.json を編集してトークンを設定してください")
            return False
        
        print("✅ 設定ファイル: OK")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ 設定ファイルの形式が正しくありません: {e}")
        return False
    except Exception as e:
        print(f"❌ 設定ファイルの読み込みエラー: {e}")
        return False

def test_output_directory():
    """出力ディレクトリのテスト"""
    print("\n🔍 出力ディレクトリテスト...")
    
    try:
        import json
        with open("notion_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        output_dir = config["notion"].get("default_output_dir", "notion_downloads")
        output_path = Path(output_dir)
        
        # ディレクトリが存在しない場合は作成
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 出力ディレクトリを作成しました: {output_path}")
        
        # 書き込み権限をテスト
        test_file = output_path / "test_write.txt"
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            test_file.unlink()  # テストファイルを削除
            print(f"✅ 出力ディレクトリ: OK ({output_path})")
            return True
        except Exception as e:
            print(f"❌ 出力ディレクトリに書き込みできません: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 出力ディレクトリテストエラー: {e}")
        return False

def test_api_connection():
    """API接続テスト"""
    print("\n🔍 API接続テスト...")
    
    try:
        import json
        import re
        from notion_downloader import NotionDownloader
        
        def resolve_environment_variables(value):
            """文字列内の環境変数を解決する"""
            if isinstance(value, str):
                pattern = r'\$\{([^}]+)\}'
                def replace_env_var(match):
                    env_var = match.group(1)
                    return os.getenv(env_var, match.group(0))
                return re.sub(pattern, replace_env_var, value)
            return value
        
        with open("notion_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        token = resolve_environment_variables(config["notion"]["token"])
        downloader = NotionDownloader(token)
        
        # 簡単なAPI呼び出しテスト
        try:
            # 検索APIを呼び出してテスト
            pages = downloader.search_pages("")
            print(f"✅ API接続: OK (利用可能なページ数: {len(pages)})")
            return True
        except Exception as e:
            if "401" in str(e):
                print("❌ API接続: 認証エラー (トークンを確認してください)")
            elif "403" in str(e):
                print("❌ API接続: 権限エラー (ページに統合を追加してください)")
            else:
                print(f"❌ API接続エラー: {e}")
            return False
            
    except Exception as e:
        print(f"❌ API接続テストエラー: {e}")
        return False

def run_all_tests():
    """全てのテストを実行"""
    print("🧪 Notionダウンローダーテスト開始\n")
    
    tests = [
        ("モジュールインポート", test_imports),
        ("設定ファイル", test_config_file),
        ("出力ディレクトリ", test_output_directory),
        ("API接続", test_api_connection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"📋 {test_name}テスト...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 テスト結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 全てのテストが通過しました！")
        print("Notionダウンローダーを使用できます。")
    else:
        print("⚠️  一部のテストが失敗しました。")
        print("上記のエラーメッセージを確認して修正してください。")
    
    return passed == total

def show_usage_examples():
    """使用例を表示"""
    print("\n📖 使用例:")
    print("1. セットアップ手順の表示:")
    print("   python notion_helper.py setup")
    print()
    print("2. ページのダウンロード:")
    print("   python notion_helper.py page <page_id>")
    print()
    print("3. 検索してダウンロード:")
    print("   python notion_helper.py search \"検索クエリ\"")
    print()
    print("4. データベース全体のダウンロード:")
    print("   python notion_helper.py database <database_id>")

if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        show_usage_examples()
    else:
        print("\n🔧 トラブルシューティング:")
        print("1. pip install requests を実行")
        print("2. notion_config.json でトークンを設定")
        print("3. Notionページに統合を追加")
        print("4. 再度テストを実行: python test_notion_downloader.py") 