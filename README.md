# bank-auto-transfer

銀行口座に自動でログインし、振込を実行するウェブスクレイピングツールです。Python と Selenium を使用して構築されており、Docker または仮想環境 (venv) を使用してセットアップできます。

## 特徴

- 銀行口座への自動ログイン
- 振込の実行
- 環境変数を通じて設定可能

## 必要条件

- Python 3.10 以降
- Docker

## セットアップ

### 仮想環境 (venv) 

ヘッドフルモードで動作させるための環境を構築します。

```bat
cd [任意のパス]
mkdir [任意のフォルダ名]
cd [任意のフォルダ名]
python -m venv .venv
```

仮想環境をアクティベートした状態で、必要なモジュールを追加します。

```bat
.venv\Scripts\activate
pip install selenium==4.22.0
pip install python-dotenv==1.0.1
```

### 仮想環境 (Docker) 

Docker イメージをビルドします。

```bash
docker compose up -d
```

### 環境変数

いくつかの環境変数を必要とします。プロジェクトのルートディレクトリに `.env` ファイルを作成し、以下の変数を設定してください:

| 変数名      | 説明  |
|-------------|------------------------------------------------------|
| MODE_TEST   | 1:振込無しで実行,0:振込ありで実行                    |
| WAIT_TIME   | 要素取得のための待機時間                             |
| KAIIN_NO    | ログイン用会員番号                                   |
| PASSWORD    | ログイン用パスワード                                 |
| KEY_MAP_STR | JSON化した振込用認証キー一覧 (例：'{"Ａ－１":"xx"}')  |
| LOGIN_URL   | ログインページURL                                   |



## 実行

```bash
# ヘッドフルモードで実行
python -m src.main

# ヘッドレスモードで実行
docker exec -it bank-auto-transfer python -m src.main
```
