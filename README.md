# Notion API ドキュメントダウンローダー

Notion API を使用してドキュメントをダウンロードし、Obsidian ディレクトリに Markdown ファイルとして保存するツールです。

## 🚀 機能

- ✅ Notion ページの Markdown 変換
- ✅ データベース全体の一括ダウンロード
- ✅ ページ検索機能
- ✅ リッチテキスト形式の保持
- ✅ 画像、リンク、コードブロックの対応
- ✅ Obsidian 互換の Markdown 出力
- ✅ メタデータの自動追加

## 📋 必要なもの

- Python 3.7 以上
- Notion API トークン
- ダウンロードしたいページへのアクセス権限

## 🚀 インストール

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. リポジトリのクローン

```bash
git clone https://github.com/hirontan/notion-downloader.git
cd notion-downloader
```

## 🛠️ セットアップ

### 1. 依存関係のインストール

```bash
pip install requests
```

### 2. Notion 統合の作成

1. [Notion Integrations](https://www.notion.so/my-integrations) にアクセス
2. 「New integration」をクリック
3. 統合の名前を入力（例: Obsidian Sync）
4. Submit をクリック
5. Internal Integration Token をコピー

### 3. .env ファイルの作成とトークン設定

1. サンプルファイルから.env をコピー

```bash
cp .env.sample .env
```

2. .env ファイルをエディタで開き、`NOTION_TOKEN`に自分の Notion トークンを設定してください。

```env
NOTION_TOKEN=your_actual_token_here
```

### 4. ページへの統合追加

ダウンロードしたいページで：

1. ページ右上の「...」をクリック
2. 「Add connections」を選択
3. 作成した統合を選択

## 📖 使用方法

### ヘルパースクリプト（推奨）

```bash
# セットアップ手順の表示
python notion_helper.py setup

# 単一ページのダウンロード
python notion_helper.py page <page_id>

# データベース全体のダウンロード
python notion_helper.py database <database_id>

# 検索してダウンロード
python notion_helper.py search "検索クエリ"
```

### 直接実行

```bash
# 単一ページのダウンロード
python notion_downloader.py --token <your_token> --page-id <page_id>

# データベースのダウンロード
python notion_downloader.py --token <your_token> --database-id <database_id>

# ページ一覧の表示
python notion_downloader.py --token <your_token> --list-pages

# 検索結果の表示
python notion_downloader.py --token <your_token> --list-pages --search "検索クエリ"
```

## 🔍 ページ ID の取得方法

### 方法 1: URL から取得

Notion ページの URL: `https://notion.so/workspace/page-id`

- `page-id` の部分がページ ID です

### 方法 2: 検索機能を使用

```bash
python notion_helper.py search "ページタイトル"
```

## 📁 出力ファイル

ダウンロードされたファイルは以下の形式で保存されます：

```markdown
# ページタイトル

**作成日**: 2024-12-19 15:30:45
**Notion ページ ID**: 12345678-1234-1234-1234-123456789abc
**URL**: https://notion.so/12345678123412341234123456789abc

---

ページの内容がここに表示されます...
```

## 🎯 対応しているブロックタイプ

- 📝 段落 (paragraph)
- 📋 見出し (heading_1, heading_2, heading_3)
- 📝 リスト (bulleted_list_item, numbered_list_item)
- ☑️ チェックボックス (to_do)
- 💻 コードブロック (code)
- 💬 引用 (quote)
- 💡 コールアウト (callout)
- ➖ 区切り線 (divider)
- 🖼️ 画像 (image)
- 📑 目次 (table_of_contents)

## 🔧 カスタマイズ

### 設定ファイルの詳細

```json
{
  "notion": {
    "token": "your_token",
    "default_output_dir": "notion_downloads",
    "supported_block_types": [...]
  },
  "obsidian": {
    "vault_path": ".",
    "attachments_folder": "attachments",
    "templates_folder": "templates"
  },
  "markdown": {
    "include_metadata": true,
    "include_notion_links": true,
    "preserve_formatting": true
  }
}
```

### 出力ディレクトリの変更

```bash
# ヘルパースクリプトの場合
# notion_config.json の default_output_dir を変更

# 直接実行の場合
python notion_downloader.py --token <token> --page-id <id> --output-dir "custom/path"
```

## 🚨 トラブルシューティング

### よくあるエラー

1. **401 Unauthorized**

   - トークンが正しく設定されているか確認
   - ページに統合が追加されているか確認

2. **404 Not Found**

   - ページ ID が正しいか確認
   - ページが存在するか確認

3. **403 Forbidden**
   - ページへのアクセス権限があるか確認
   - 統合がページに追加されているか確認

### デバッグモード

```bash
# 詳細なエラー情報を表示
python notion_downloader.py --token <token> --page-id <id> --verbose
```

## 📝 例

### プロジェクト計画ページのダウンロード

```bash
python notion_helper.py page 12345678-1234-1234-1234-123456789abc
```

### タスクデータベース全体のダウンロード

```bash
python notion_helper.py database 87654321-4321-4321-4321-987654321cba
```

### 「会議」を含むページを検索してダウンロード

```bash
python notion_helper.py search "会議"
```

## 🤝 貢献

バグ報告や機能要望は、GitHub の Issues でお知らせください。

## 📄 ライセンス

MIT License

## 🔗 関連リンク

- [Notion API Documentation](https://developers.notion.com/)
- [Obsidian Documentation](https://obsidian.md/)
- [Markdown Guide](https://www.markdownguide.org/)

## 🐍 Python のインストールと仮想環境の作成

### 1. pyenv で Python をインストール

```bash
# 最新の安定版（例: 3.12.8）をインストール
pyenv install 3.12.8

# プロジェクトディレクトリでバージョンを固定
cd /path/to/your/project
pyenv local 3.12.8
```

### 2. 仮想環境(venv)の作成と有効化

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化（macOS/Linux）
source venv/bin/activate

# 仮想環境の有効化（Windows）
venv\Scripts\activate

# 仮想環境の無効化
deactivate
```

## 🧪 動作確認テスト

セットアップや環境移行後、Notion ダウンローダーが正しく動作するか確認したい場合は、以下のコマンドでテストを実行できます。

```bash
python test_notion_downloader.py
```

このスクリプトは、依存パッケージ・設定ファイル・API 接続などを自動でチェックします。

全てのテストが「✅」で通れば、Notion ダウンローダーを安心して利用できます。
