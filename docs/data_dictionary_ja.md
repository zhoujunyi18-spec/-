# データ辞書と来歴

## 取得データ

`data/private/<appid>/page_*.json` はAPI応答の取得時原本。`reviews.jsonl` はレビューIDで重複を除いた原文。`manifest.json` は各ページのURL・時刻・ハッシュ、停止理由、件数を記録する。privateは公開対象外。

主キーは recommendationid（文字列）。appid、review、language、timestamp_created、timestamp_updated、voted_up、steam_purchase、received_for_free、refunded等をAPIの有無に応じて保持。返っていないフィールドを偽または0で埋めない。author.playtime_at_reviewとplaytime_foreverは異なる時点の分数。author.steamidやハードウェア情報は本分析に不要であり公開しない。

## 公開ラベル

`data/pilot_labels_unvalidated.json` は意味検証前のAIラベル。main_case=trueは正式4作品120件、falseは除外SO2R診断30件。推薦フラグは抽出後の補助分析用に結合。

currentは要素コードごとの現在極性。comparisonsは要素、参照版、関係、相対方向、比較関係への価値評価の配列。no_changeは性質の維持。positiveと同義ではない。comparison_valenceは原文の比較表現への賛否だが、全体の推薦とは異なる。除外候補の診断ラベルにある旧新音声の併存表現などは境界確認用であり、正式推定に用いない。

原文根拠と文字位置はローカルの `data/private/pilot/annotations_with_evidence.json` に保管。位置はPython文字列上の0始まり・終了位置非包含であり、UTF-8バイト位置ではない。元の改行を保持。文書化のための空白正規化を照合に使った場合も、保存した根拠は実際の原文部分文字列。

`data/sample_manifest.json` は固定ハッシュ選択の種とID。先導用150件には除外SO2R30件が含まれる。人手検証用は正式4作品200件で、先導全件と非重複。除外候補FFVII REBIRTHは先導・検証に含めない。

## 集計

`results/data_audit.json` は正式4作品の全量取得監査。`initial_case_audit.json` は初期候補監査の履歴。`replacement_candidates.json` は同条件での候補8配信ページの初回件数監査であり、全件取得済みを意味しない。

`main_data_audit.json` は短文・ASCII簡易診断などを追加した値。`pilot_aspects.csv` は要素別に現在評価数・比較数・両者の共通部分・方向を集計。各方向の件数はレビュー単位で重複集約している。比較に維持と変更の双方があれば優劣方向の明示を優先するが、元タプルも保存する。

`pilot_recommendation_comparison.json` のWilson区間は標本誤差の参考であり、注釈誤差・選択バイアス・同一投稿者の依存を補正していない。全量推薦数には標本区間を付けない。

`pilot_sensitivity.json` の保守的除外は曖昧事例の影響診断。すべての曖昧さを網羅した下限推定ではなく、採否による因果的効果でもない。
