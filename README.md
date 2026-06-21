# slack-bot

Slackワークスペース内の公開チャンネルの投稿を取得し，一つのチャンネルに同じ内容を投稿するbotです．  
[slackdump](https://github.com/rusq/slackdump) を用いたバックアップ機能つきです．  
バックアップの表示に [Rocket.chat](https://rocket.chat/) を使用することができます．

## 要件

- Linux または macOS (WSLも可)
- Windows の場合は [BusyBox](https://github.com/rmyorston/busybox-w32)
  - `busybox64u.exe` をインストールし，環境変数 PATH に追加しておく．
- Python 3.8 以上

## セットアップ手順

### 作業環境の準備

1. リポジトリをクローンする．
   ```bash
   git clone https://github.com/NAFT-LinkSpace/slack-bot
   cd slack-bot
   ```
1. スクリプトを実行し環境構築
    ```bash
    # Windows の場合 `busybox64u sh` の実行後
    chmod +x ./without_docker/setup.sh
    ./without_docker/setup.sh
    ```

### バックアップを取る準備

1. ブラウザでボットを導入したい Slack ワークスペースにログインする．
1. ワークスペースの画面で開発者用ツールを開く
1. コンソールタブで以下のコマンドを実行し，`xoxc-` で始まるトークンを控えておく．
   ```javascript
   JSON.parse(localStorage.localConfig_v2).teams[document.location.pathname.match(/^\/client\/(T[A-Z0-9]+)/)[1]].token
   ```
1. **Application > Cookies > https://app.slack.com** を選択し，`d` という名前のクッキーの値(`xoxd-` で始まる)を控えておく．

### Slack Appの導入

1. [slack apiのページ](https://api.slack.com/apps)にアクセスし，**Create New App** から新しいアプリを作成する．
1. **from an app manifest**を選択し，ボットを導入するワークスペースを選択する．
1. YAMLタブを選択し，`manifest.yaml` の内容をコピペする．
1. **Create**
1. **Settings > Basic Information** から **Install to Workspace** を選択し，ワークスペースにインストールする．
1. **App-Level Tokens** の **Generate Token and Scopes** から `connections:write` スコープを追加し，**Generate** を押してトークンを発行する．
1. **App-level Token** を控えておく．
1. **Features > OAuth & Permissions > OAuth Tokens** から **Bot User OAuth Token** を控えておく．

### (任意) Rocket.Chatの導入

1. [Rocket.Chatの公式サイト](https://rocket.chat/install)を参考に，Rocket.Chatを導入する．
   Step 1, Step 2, Step 3, Step 5のみでいい．
1. http://localhost:3000 にアクセスし，アカウントとワークスペースを作成する．
1. ユーザーのアイコンをクリックし，**Preferences > Personal Access Tokens** を選択する．
1. 適当な名前をつけて **Add** を押し，トークンを発行し，**Token** と **Your user Id** を控えておく．

なお，使いやすさのために以下の項目を設定しておくといい．
1. 3点アイコン(Administration)をクリックし，**Workspace > Settings > Search > Default provider** から **Global search** をオンにする．
1. **Workspace > Settings > Message > Always Search Using RegExp** をオンにする．

### 環境変数の設定

1. `.env.example` をコピーして `.env` ファイルを作成する．
1. `.env` ファイルを以下のように設定する．
   1.  `SLACK_BOT_TOKEN` に **Bot User OAuth Token**
   1.  `SLACK_APP_TOKEN` に **App-level Token**
   1.  `SLACK_TOKEN` にワークスペースから取得した **xoxc-** で始まるトークン
   1.  `SLACK_COOKIE` にワークスペースから取得した **xoxd-** で始まるトークン
   1.  `POST_CHANNEL_NAME` に投稿先のチャンネル名
1. Rocket.Chat を使用しない場合は, `ROCKETCHAT_URL`, `ROCKETCHAT_USER_ID`, `ROCKETCHAT_TOKEN` の行を削除するかコメントアウトする．
1. Rocket.Chat を使用する場合は, 以下のように設定する．
   1. `ROCKETCHAT_URL` に Rocket.Chat の URL (localで動かす場合は変えなくていい)
   1. `ROCKETCHAT_USER_ID` に **Your user Id**
   1. `ROCKETCHAT_TOKEN` に **Token**

## 実行

```bash
# Windows の場合 `busybox64u sh` の実行後
chmod +x ./without_docker/run.sh
./without_docker/run.sh
```
