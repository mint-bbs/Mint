<div align="center">
<img alt="Mint BBS" src="./static/img/mint.png"><br>
</div>

[![](https://discord.com/api/guilds/1218841426918510632/widget.png)](https://discordsrv.com/discord "Discord")
[![](https://img.shields.io/github/release/mint-bbs/mint.svg)](https://github.com/mint-bbs/mint/releases/latest "Latest release")
![](https://img.shields.io/github/languages/code-size/mint-bbs/mint.svg "Code size in bytes")
[![](https://img.shields.io/github/contributors/mint-bbs/mint.svg)](https://github.com/mint-bbs/mint/graphs/contributors "GitHub contributors")
[![](https://img.shields.io/github/license/mint-bbs/mint.svg)](https://github.com/mint-bbs/mint/blob/master/LICENSE "License")

<center>Mintは2ch互換掲示板を運営することができるソフトウェアです</center>

## Features

- 2ch 専用ブラウザとの互換性あり
- スレッド・レスの自動更新
- 高速な書き込み
- わかりやすい UI

## Schedule

- レスを削除する機能
- プラグイン機能
- テーマ機能

## How To Install

### 必要なもの

- Python 3.11 (3.12 では未テストです)
  - なお、PyPy など、Cpython 以外の Python 実装は利用できません。
- PostgreSQL (15.6 でテスト済み)

### .env ファイルを作成

`.env.sample` ファイルを `.env` ファイルとしてコピーし、編集します。

```env
dsn=postgresql://<username>:<password>@<address>:<port>/<database>
metaid=0 ←通常は変更しない
admin_request_password=<管理者リクエストを送信するためのパスワード>
```

### 仮想環境の作成

`.env` ファイルを保存したら、仮想環境を作成します。

```ps1
# Windows
py -m venv venv
# Mac / Linux
python3 -m venv venv
```

処理が終了したら、仮想環境に入ります。

```bash
# Windows
./venv/Scripts/activate
# Mac / Linux
source ./venv/bin/activate
```

### 必要なライブラリのインストール

仮想環境を作成できたら、必要なライブラリのインストールに入ります。

```ps1
# Windows
py -m pip install -r requirements.txt
# Mac / Linux
python3 -m pip install -r requirements.txt
```

### データベースの初期化

必要なライブラリのインストールが完了したら、データベースの初期化を行います。

```ps1
# Windows
py -m alembic upgrade head
# Mac / Linux
python3 -m alembic upgrade head
```

### 起動

データベースの初期化が終了したら、起動します。

```ps1
# Windows
py -m uvicorn main:app --host 0.0.0.0 --port <ポート>
# Mac / Linux
python3 -m uvicorn main:app --host 0.0.0.0 --port <ポート>
```

### アドミンユーザーの作成

http://localhost:<ポート>/admin にアクセスし、希望するユーザー名・パスワード・管理者リクエストを送信するためのパスワードを入力し、ログインします。

インストール終了です。「メタデータ編集」からサイト名を変更したり、「板設定」から板を追加したりしてください。お疲れ様でした。
