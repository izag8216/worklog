<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=wave&color=2D5A27&fontColor=FDF6E3&height=180&text=worklog&fontSize=45&fontAlignY=42&desc=%E3%82%BD%E3%83%AD%E8%B5%B7%E6%A5%AD%E5%AE%B6%E5%90%91%E3%81%91%E6%97%A5%E6%AC%A1%E3%82%A2%E3%82%AF%E3%83%86%E3%82%A3%E3%83%93%E3%83%86%E3%82%A3%E9%9B%86%E8%A8%88%E3%83%84%E3%83%BC%E3%83%AB&descSize=16&descAlignY=62&descAlign=center&animation=fadeIn" alt="worklog header" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue?style=flat-square" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License" />
  <img src="https://img.shields.io/badge/tests-47%20passing-brightgreen?style=flat-square" alt="Tests" />
  <img src="https://img.shields.io/badge/coverage-91%25-brightgreen?style=flat-square" alt="Coverage" />
</p>

[English](README.md) | Japanese

**worklog** は、gitコミット、手動メモ、その他のローカルソースから日々のアクティビティを自動集計し、統合タイムラインを出力するCLIツールです。クラウドサービス不要、API不要 -- ローカルデータだけで完結します。

## 特徴

- **Git アクティビティ収集** -- 複数のローカルgitリポジトリをスキャンし、作者・日付でコミットを抽出
- **手動アノテーション** -- タグ付きのフリーテキストメモを任意の日付に追加
- **統合タイムライン** -- 全ソースを時系列のデイリーサマリーに統合
- **複数出力形式** -- ターミナル（rich）、Markdown、JSON、CSV
- **エクスポート** -- レポートをファイルに保存してアーカイブや共有に
- **クラウド依存ゼロ** -- SQLite + git でローカル完結

## インストール

```bash
pip install worklog
```

ソースからインストール:

```bash
git clone https://github.com/izag8216/worklog.git
cd worklog
pip install -e .
```

## クイックスタート

```bash
# 初期設定（対話式）
worklog init

# 今日のアクティビティサマリー
worklog today

# 今週のサマリー
worklog week

# 今月のサマリー
worklog month

# 日付範囲指定
worklog log --from 2026-04-01 --to 2026-04-18

# 手動メモを追加
worklog annotate --note "v2.0を本番にデプロイ" --tag release

# ファイルにエクスポート
worklog export --from 2026-04-01 --to 2026-04-30 --format markdown --output april-log.md
worklog export --from 2026-04-01 --to 2026-04-30 --format json --output april-log.json
worklog export --from 2026-04-01 --to 2026-04-30 --format csv --output april-log.csv
```

## 設定

設定ファイルは `~/.worklog/config.yaml` に保存されます:

```yaml
repos:
  - path: ~/projects/my-project
  - path: ~/projects/other-repo

author:
  email: user@example.com

week_start: monday    # monday or sunday
export_dir: ~/.worklog/exports
```

## コマンド一覧

| コマンド | 説明 |
|---------|------|
| `worklog init` | 設定ファイルを対話的に作成 |
| `worklog today` | 今日のアクティビティサマリー |
| `worklog week` | 今週のサマリー |
| `worklog month` | 今月のサマリー |
| `worklog log --from 日付 --to 日付` | 日付範囲指定 |
| `worklog annotate --note テキスト` | 手動メモを追加 |
| `worklog notes` | メモ一覧表示 |
| `worklog export --from 日付 --to 日付 --format 形式` | ファイルにエクスポート |
| `worklog repos` | 設定済みリポジトリ一覧とステータス |
| `worklog config` | 現在の設定を表示 |

## 出力例

```
2026-04-18 (Today)
─────────────────
09:15  [git] my-project: Refactor auth module (#42)
10:30  [note] Code review session with team
11:00  [git] other-repo: Fix pagination bug
14:00  [git] my-project: Add export feature (#43)
15:30  [note] Deployed v2.0 to production  [release]

5 activities | 3 commits | 2 notes
```

## 開発

```bash
# 開発依存をインストール
pip install -e ".[dev]"

# テスト実行
pytest tests/ -v

# カバレッジ付きテスト
pytest tests/ -v --cov=worklog --cov-report=term-missing
```

## ライセンス

MIT License -- 詳細は [LICENSE](LICENSE) を参照。
