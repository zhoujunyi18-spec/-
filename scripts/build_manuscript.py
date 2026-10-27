"""初稿本文に参考文献と実例索引を結合する。"""
import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    text=(ROOT/'manuscript/draft_ja.md').read_text(encoding='utf-8')
    text=text.replace('### 4.2 言語と短文の扱い','![図1：取得コーパスの推薦フラグ](../figures/01_corpus_recommendation.svg)\n\n### 4.2 言語と短文の扱い')
    text=text.replace('### 5.2 現在評価の方向','![図2：先導標本の現在評価被覆（未検証AIラベル）](../figures/02_pilot_coverage_unvalidated.svg)\n\n### 5.2 現在評価の方向')
    text+='\n\n## 参考文献\n\n'
    for r in json.loads((ROOT/'literature/references.json').read_text(encoding='utf-8')):
        text+=f"［{r['id']}］{r['citation']} [{r['doi'] or '公開資料'}]({r['url']})\n\n"
    text+='''## 付録A：判断を追跡するための実例索引

以下は先導注釈の検討例であり、正解データではない。レビューIDは公開ラベルに対応し、全文・証拠文字位置はローカル原本に保存する。

|標本ID|検討内容|暫定的な扱い|
|---|---|---|
|P005|原作経験と現在のエンディング等への好意|性質の対照なし。原作比較に数えない|
|P028|無印のダンジョンの苦しさと現在の負担低減|相対肯定あり。現在の絶対的な肯定は補わない|
|P071|旧版に比べ難易度が上がったという記述|変化の方向あり、価値方向は未評価|
|P083|情報の分かりやすさの改善と別の情報表示への不満|上位UIで共存するが、同一下位対象の不一致とは即断しない|
|P098|敵AIや難易度の変化|難しくなったことを退歩に自動変換しない|
|P112|不便さがそのままという不満|現在負、保持。相対的な退歩とは区別|
|P116|レベル上げが容易になったという対照|比較は採用するが、明示的好意が弱いため相対方向未評価|
|P133|FCに対する移動・戦闘等の変更を包括的に肯定|列挙の評価範囲に曖昧さがあり感度分析対象|
|P146|旧版の戦闘・サブクエストのテンポを見直したという対照|具体的旧版比較あり。元の魅力の保持と実装の変更を分ける|

付録Bの全要素表は [先導集計](../results/pilot_report_ja.md) と [CSV](../results/pilot_aspects.csv) を参照。文献の確認範囲は [照合台帳](../literature/references_ja.md) を参照。
'''
    (ROOT/'manuscript/thesis_with_references_ja.md').write_text(text,encoding='utf-8')
    print('manuscript with bibliography:',len(text),'characters')
if __name__=='__main__':main()
