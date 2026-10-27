# 再現手順

Python 3.11以上を想定。取得・標本抽出・集計・公開結果検査は標準ライブラリのみで実行できる。PDF本文抽出にpypdf、図にmatplotlibを使う。ネットワークが必要な工程と、ローカルだけで行う検査を分ける。

## 公開ファイルだけで行う検査

```text
python scripts/verify_public.py
```

公開AIラベルから現在極性・要素被覆・比較被覆等の196項目を再計算し、保存した表と一致するか検査する。意味的な妥当性や人手一致度を検査するものではない。

## データを再取得する場合

```text
python scripts/collect_steam.py
python scripts/prepare_samples.py
```

Steam公式の現行APIを利用する。原本・カーソル・ハッシュをdata/privateへ保存。ネットワークエラーはバックオフし、カーソル停滞は空ページ終了と区別する。取得時点に公開状態が変わっていれば同じID・本文が揃うとは限らない。投稿締切を指定しても更新後本文を過去の本文へ戻すことはできない。

初期SO2Rの診断用原本は現行収集対象に含めない。履歴を含む先導150件を完全に再生成するには、そのローカル原本も必要となる。主分析の再計算には公開ラベルで足りる。

## 私的原本がある場合

```text
python scripts/analyze_pilot.py
python scripts/verify_public.py
python scripts/make_figures.py
```

analyze_pilot.pyはローカルの原文と対話による注釈原票を必要とする。全文に対する根拠位置を確認するが、固定モデルの再実行ではない。正式なLLM抽出の実行スクリプトは未実装であり、モデル・設定・API利用条件を確定後に追加する。

## 文献

```text
python scripts/build_bibliography.py
python scripts/fetch_literature.py
```

出版社のアクセス制限や取得エラーを記録する。Crossrefに見つからないことを論文不存在とは解釈せず、J-STAGEや出版社の原ページを照合する。E10/E11のローカルPDFは著者プレプリントであり、誌面最終版との差に注意する。

既存PDFを再利用する場合はキャッシュ利用として扱う。取得記録の日時はスクリプトの処理時刻であり、キャッシュ原本の初取得時刻を上書きして履歴を再現するものではない。
