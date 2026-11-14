# AGENTS.md

見た目はDESIGN.mdにしたがう。

- このディレクトリが ORBITAL FORGE 専用のリポジトリ。親ディレクトリや他のポートフォリオをコミットに含めない。
- 静的 HTML / CSS / JavaScript を `dist/` に置く。フレームワークやパッケージのインストールは不要。HTMLの生成はPython標準ライブラリだけで行う。
- 表示名は最新のユーザー資料に合わせ `ORBITAL FORGE` / `オービタルフォージ株式会社` とする。リポジトリと公開URLの `rbital-forge` は変更しない。
- `content/company.json` がユーザー提供の2038年の創作設定。企業・事業・実績・数値が架空であることを明記する。提供されていない実績、顧客名、連絡先、外部URLを追加しない。
- 内容変更は `content/company.json`、構造変更は `templates/index.html`。`python3 scripts/build-site.py` で `dist/index.html` を再生成する。生成HTMLだけを直接編集しない。
- `python3 scripts/build-site.py --check`、`python3 scripts/check-site.py`、`node --check dist/site.js`、`node scripts/test-interactions.cjs` で確認する。
- コンピューターユーズの可否はユーザーの最新指示に従う。コード・HTTPの検証と実画面の検証を区別して報告する。
- リポジトリは `moai-okinawa/rbital-forge`（Public）。既存の `portfolio-kawasakiZ` を上書きしない。
