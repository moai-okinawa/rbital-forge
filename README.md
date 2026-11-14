# RBITAL FORGE

RBITAL FORGE の新しいコンセプトポートフォリオです。HTML・CSS・JavaScriptのみの静的サイトで、ビルドやパッケージのインストールは不要です。

**掲載している作品・紹介文は仮の内容です。** ORBIT / RELAY / FIELD は架空のサンプルであり、実案件・稼働中のサービスではありません。

## ローカルで開く

リポジトリのディレクトリで実行します。

```sh
python3 -m http.server 8000 --directory dist --bind 127.0.0.1
```

`http://127.0.0.1:8000` を開きます。停止は `Ctrl+C`。`dist/index.html` を直接開いても閲覧できます。

## 機能

- PC・タブレット・スマートフォン向けレイアウト
- 作品のカテゴリー絞り込みと結果件数の読み上げ
- キーボードでも操作できる作品詳細（JavaScriptなしでも利用可能）
- スマートフォン用の開閉メニュー
- フォーカス表示、スキップリンク、動きを減らす設定への対応

## 編集するファイル

| ファイル | 内容 |
| --- | --- |
| `dist/index.html` | 表示名・紹介文・作品・ナビゲーション |
| `dist/style.css` | 色・文字・余白・レスポンシブ設定 |
| `dist/site.js` | 絞り込み・メニューの操作 |
| `dist/assets/` | オリジナルSVGとアイコン |
| [DESIGN.md](DESIGN.md) | デザインの基準・実装値・アクセシビリティ |
| [AGENTS.md](AGENTS.md) | このリポジトリを編集する際のルール |

デザインの参照元は [VoltAgent/awesome-design-md の Expo DESIGN.md](https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/expo/DESIGN.md)。Expo公式サイトや公式ポートフォリオではありません。InterはGoogle Fontsから読み込み、日本語は端末のサンセリフ体へフォールバックします。

## 検証

```sh
python3 scripts/check-site.py
node --check dist/site.js
node scripts/test-interactions.cjs
```

HTMLの参照・画像・見出し・構造、SVG、配色のコントラスト、フィルターとメニューの動作をコードで確認します。これは実際のブラウザのレイアウト、読み上げ、キーボード操作の確認を代替しません。サイトの実画面確認は未実施です。

## GitHub

リポジトリ: [moai-okinawa/rbital-forge](https://github.com/moai-okinawa/rbital-forge)（Public）。このフォルダーだけが対象です。親フォルダーや `portfolio-kawasakiZ` は含めません。

サイト: [RBITAL FORGE](https://moai-okinawa.github.io/rbital-forge/)

push時には `Check static site` のGitHub Actionsが上記のコード検証を実行します。

公開元は **Settings → Pages → Source → GitHub Actions** です。更新を再公開するときは、変更をpushした後、**Actions → Deploy to GitHub Pages → Run workflow** で `main` を選んで実行してください。Pages用ワークフローは `workflow_dispatch` による手動起動です。
