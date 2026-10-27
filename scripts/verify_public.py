"""公開ラベルのみから主要集計を再計算し、保存表との一致を確認。"""
import csv,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    rows=json.loads((ROOT/'data/pilot_labels_unvalidated.json').read_text(encoding='utf-8'))
    rows=[r for r in rows if r['main_case']]
    saved=list(csv.DictReader((ROOT/'results/pilot_aspects.csv').open(encoding='utf-8-sig')))
    assert len(rows)==120 and len({r['recommendationid'] for r in rows})==120
    checks=0
    for s in saved:
        app=int(s['appid']);a=s['aspect'];g=[r for r in rows if r['appid']==app]
        evaluated=[r for r in g if a in r['current']]
        compared=[r for r in g if any(c['aspect']==a for c in r['comparisons'])]
        actual={'n_reviews':len(g),'evaluated':len(evaluated),'compared':len(compared),'compared_and_evaluated':sum(a in r['current'] for r in compared)}
        for direction in ['positive','negative','mixed']:actual[direction]=sum(r['current'][a]==direction for r in evaluated)
        for k,v in actual.items():assert int(s[k])==v,(app,a,k,v,s[k]);checks+=1
    sample=json.loads((ROOT/'data/sample_manifest.json').read_text(encoding='utf-8'))
    assert not (set(sample['pilot_ids'])&set(sample['validation_ids']))
    assert len(sample['validation_ids'])==200
    assert len(json.loads((ROOT/'literature/references.json').read_text(encoding='utf-8')))==20
    # 全量監査の整合性と主要対象の除外規則。
    audit=json.loads((ROOT/'results/data_audit.json').read_text(encoding='utf-8'))
    assert {r['appid'] for r in audit}=={2161700,2455640,2701660,3375780}
    assert sum(r['n'] for r in audit)==4792
    for r in audit:assert r['n']==r['positive']+r['negative']==r['api_total_matching'];assert r['stop']=='empty_page';assert r['duplicates']==0
    print(f'PASS: {checks} aggregate checks; 120 main pilot labels; 200 disjoint validation IDs; 20 references; 4792 audited reviews.')
    print('This verifies arithmetic and files, not semantic accuracy or human agreement.')
if __name__=='__main__':main()
