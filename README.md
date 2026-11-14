# ORBITAL FORGE

2038年を舞台にした架空の宇宙産業企業 **ORBITAL FORGE（オービタルフォージ株式会社）** のコンセプトサイトです。ユーザー提供の企業設定をもとに、12事業・77の提供サービス・主力施設FORGE-01・6つの代表実績・19の成果項目を掲載しています。

**企業・事業・実績・数値はすべて創作です。** 図版やMISSION OSの端末画面もコンセプトイメージであり、実在する施設や稼働中のサービスを示しません。未提供の顧客名、連絡先、外部サービスURLは追加していません。

公開ファイルはHTML・CSS・JavaScriptのみです。内容とテンプレートからPython標準ライブラリでHTMLを生成します。フレームワークやパッケージのインストールは不要です。

## ローカルで開く

リポジトリのディレクトリで実行します。

```sh
python3 scripts/build-site.py
python3 -m http.server 8000 --directory dist --bind 127.0.0.1
```

[ローカルサイト](http://127.0.0.1:8000)を開きます。停止は `Ctrl+C`。生成済みの `dist/index.html` を直接開いても閲覧できます。

## 機能

- PC・タブレット・スマートフォン向けのレイアウト
- 12事業を「製造・研究」「建設・運用」「輸送・循環」「月面開発」で絞り込み、結果件数を読み上げ
- 事業詳細と実績の成果をネイティブの `details` / `summary` で開閉（JavaScriptなしでも閲覧可能）
- FORGE-01のオリジナル図版、設備一覧、2031〜2038年の代表実績、企業概要
- スマートフォン用の開閉メニュー、スキップリンク、フォーカス表示、動きを減らす設定への対応

## 編集するファイル

内容の流れは **`content/company.json` → `templates/index.html` → `scripts/build-site.py` → `dist/index.html`** です。JSONに掲載内容を保持し、テンプレートと生成スクリプトで静的HTMLに組み立てます。

| ファイル | 内容 |
| --- | --- |
| `content/company.json` | ユーザー提供の企業・事業・施設・実績・数値・創作である旨の注記 |
| `templates/index.html` | ページ構造、共通見出し、端末イメージ、主要数値の抜粋表示 |
| `scripts/build-site.py` | JSONとテンプレートからHTMLを生成する処理 |
| `dist/index.html` | 公開する生成済みHTML。ここだけを直接編集しない |
| `dist/style.css` | 色・文字・余白・部品・レスポンシブ設定 |
| `dist/site.js` | 事業の絞り込み・メニューの操作 |
| `dist/assets/forge-platform.svg` | FORGE-01のオリジナルコンセプト図 |
| `dist/assets/favicon.svg` | サイトのアイコン |
| [DESIGN.md](DESIGN.md) | デザインの基準・実装値・アクセシビリティ |
| [AGENTS.md](AGENTS.md) | このリポジトリを編集する際のルール |

内容変更後は `python3 scripts/build-site.py` を実行し、生成した `dist/index.html` もコミットします。事業数や主要数値を変更するときは、テンプレート内のヒーロー・規模の一覧・施設仕様などの抜粋表示と、検証スクリプトの期待値も揃えてください。元の設定にない実績や数値を補わないでください。

デザインの参照元は [VoltAgent/awesome-design-md の Expo DESIGN.md](https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/expo/DESIGN.md)。Expo公式サイトではありません。白・黒・淡い青の構成を使い、InterはGoogle Fonts、日本語は端末のサンセリフ体で表示します。

## 検証

```sh
python3 scripts/build-site.py --check
python3 scripts/check-site.py
node --check dist/site.js
node scripts/test-interactions.cjs
```

生成HTMLとソースの一致、掲載内容の欠落、HTMLの参照・画像・見出し・構造、SVG、配色のコントラスト、フィルターとメニューの動作をコードで確認します。これは実際のブラウザのレイアウト、読み上げ、キーボード操作の確認を代替しません。2026-11-14にローカルHTTPの実ブラウザで1280px幅のヒーロー・事業一覧・詳細、390px幅のヒーロー・事業一覧・施設、320px幅のヒーロー・ヘッダーを確認しました。確認した範囲で横方向のはみ出しはありません。月面開発1件への絞り込みと全12件への復帰、Enterによる詳細開閉、モバイルメニューから施設への遷移・メニューを閉じる動作・移動先へのフォーカスも確認しました。スクリーンリーダー、動きを減らす端末設定、全ブラウザ・全幅での実機確認は未実施です。

## GitHubと公開

リポジトリ: [moai-okinawa/rbital-forge](https://github.com/moai-okinawa/rbital-forge)（Public）。表示名はORBITAL FORGEですが、リポジトリ名と公開URLの `rbital-forge` は維持します。このフォルダーだけが対象で、親フォルダーや `portfolio-kawasakiZ` は含めません。

サイト: [ORBITAL FORGE](https://moai-okinawa.github.io/rbital-forge/)

push時には `Check static site` のGitHub Actionsがコード検証を実行します。

公開元は **Settings → Pages → Source → GitHub Actions** です。変更をpushした後、**Actions → Deploy to GitHub Pages → Run workflow** で `main` を選びます。Pages用ワークフローは `workflow_dispatch` による手動起動です。生成HTMLの一致と静的ファイル・操作の検証に成功してから、`dist/` を公開します。
