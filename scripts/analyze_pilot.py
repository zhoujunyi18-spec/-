"""未検証AI先導注釈を集計する。人手検証の代用ではない。"""
import csv, hashlib, json, math, pathlib, re, statistics
ROOT=pathlib.Path(__file__).resolve().parents[1]
MAIN={2161700,2455640,2701660,3375780}
NAMES={'B':'戦闘・成長','E':'探索・誘導','N':'物語・人物','U':'UI・操作','A':'視聴覚','T':'技術的品質','O':'その他'}

def wilson(k,n):
    if not n:return [None,None]
    z=1.959963984540054;p=k/n;d=1+z*z/n
    c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,c-h),min(1,c+h)]

def evidence_span(text,quote):
    match=re.search(r'\s+'.join(re.escape(x) for x in re.split(r'\s+',quote.strip())),text)
    if not match:raise ValueError('Evidence not found: '+repr(quote))
    return dict(start=match.start(),end=match.end(),text=text[match.start():match.end()])

def main():
    sample=[json.loads(s) for s in (ROOT/'data/private/pilot/sample.jsonl').read_text(encoding='utf-8').splitlines()]
    index={r['sample_id']:r for r in sample}
    source=json.loads((ROOT/'data/private/pilot/source_annotations.json').read_text(encoding='utf-8'))
    assert len(source)==len(index)==150 and len({r['id'] for r in source})==150
    rich=[];public=[];warnings=[]
    for r in source:
        s=index[r['id']];cur={};comps=[]
        for a,(pol,ev) in r['current'].items():
            assert a in NAMES and pol in {'positive','negative','mixed'}
            evs=[ev]+r.get('extra_evidence',{}).get(a,[])
            cur[a]=dict(polarity=pol,evidence=[evidence_span(s['review'],e) for e in evs])
        for a,pol,ev,version,rel in r['comparisons']:
            span=evidence_span(s['review'],ev)
            # 保持と優劣は直交する。保持を改善・退歩に読み替えない。
            direction='no_change' if rel=='retention' else pol
            comps.append(dict(aspect=a,relative_direction=direction,comparison_valence=pol,reference_version=version,relation=rel,evidence=span))
        row=dict(sample_id=r['id'],appid=s['appid'],recommendationid=s['recommendationid'],current=cur,comparisons=comps,notes=r.get('notes',''),annotation_source='Codex conversational AI; not human; not fixed API experiment',main_case=s['appid'] in MAIN)
        rich.append(row)
        public.append(dict(sample_id=r['id'],appid=s['appid'],recommendationid=s['recommendationid'],recommended=s['voted_up'],main_case=s['appid'] in MAIN,current={a:v['polarity'] for a,v in cur.items()},comparisons=[{k:v for k,v in c.items() if k!='evidence'} for c in comps]))
    dest=ROOT/'results';dest.mkdir(exist_ok=True)
    (ROOT/'data/private/pilot/annotations_with_evidence.json').write_text(json.dumps(rich,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'data/pilot_labels_unvalidated.json').write_text(json.dumps(public,ensure_ascii=False,indent=2),encoding='utf-8')
    detail=[];supp=[];audit=[]
    for app in sorted(MAIN):
        group=[r for r in rich if r['appid']==app];n=len(group)
        allrows=[json.loads(s) for s in (ROOT/f'data/private/{app}/reviews.jsonl').read_text(encoding='utf-8').splitlines()]
        for a,name in NAMES.items():
            evaluated=[r for r in group if a in r['current']]
            compared=[r for r in group if any(c['aspect']==a for c in r['comparisons'])]
            intersect=[r for r in compared if a in r['current']]
            directions=[]
            for r in compared:
                ds={c['relative_direction'] for c in r['comparisons'] if c['aspect']==a}
                if 'mixed' in ds or {'positive','negative'}<=ds:direction='mixed'
                elif 'positive' in ds:direction='positive'
                elif 'negative' in ds:direction='negative'
                elif 'no_change' in ds:direction='no_change'
                else:direction='unevaluated'
                directions.append(direction)
            detail.append(dict(appid=app,aspect=a,aspect_ja=name,n_reviews=n,evaluated=len(evaluated),coverage=len(evaluated)/n,positive=sum(r['current'][a]['polarity']=='positive' for r in evaluated),negative=sum(r['current'][a]['polarity']=='negative' for r in evaluated),mixed=sum(r['current'][a]['polarity']=='mixed' for r in evaluated),compared=len(compared),comparison_coverage=len(compared)/n,compared_and_evaluated=len(intersect),comparison_within_evaluated=len(intersect)/len(evaluated) if evaluated else None,comparison_only=len(compared)-len(intersect),relative_positive=directions.count('positive'),relative_negative=directions.count('negative'),relative_mixed=directions.count('mixed'),relative_no_change=directions.count('no_change'),relative_unevaluated=directions.count('unevaluated')))
        for flag in [True,False]:
            subset=[r for r in group if index[r['sample_id']]['voted_up']==flag]
            k=sum(any(c['aspect'] in 'BENUA' for c in r['comparisons']) for r in subset)
            lengths=[len(index[r['sample_id']]['review']) for r in subset]
            supp.append(dict(appid=app,recommended=flag,n=len(subset),comparison_reviews=k,proportion=k/len(subset) if subset else None,wilson95=wilson(k,len(subset)),median_characters=statistics.median(lengths) if lengths else None))
        ascii_only=sum(bool(re.search('[A-Za-z]',r['review'])) and not re.search('[\u3040-\u30ff\u3400-\u9fff]',r['review']) for r in allrows)
        audit.append(dict(appid=app,n=len(allrows),positive=sum(r.get('voted_up',False) for r in allrows),negative=sum(not r.get('voted_up',False) for r in allrows),ascii_latin_without_japanese=ascii_only,n_after_ascii_screen=len(allrows)-ascii_only,median_characters=statistics.median(len(r['review']) for r in allrows),pilot_n=n,pilot_any_evaluation=sum(any(a in 'BENUA' for a in r['current']) for r in group),pilot_any_comparison=sum(any(c['aspect'] in 'BENUA' for c in r['comparisons']) for r in group)))
    for filename,rows in [('pilot_aspects.csv',detail),('pilot_recommendation_comparison.json',supp),('main_data_audit.json',audit)]:
        if filename.endswith('.csv'):
            with (dest/filename).open('w',encoding='utf-8-sig',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        else:(dest/filename).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    # 感度分析：暫定判断の難しい比較を除外しても元データは書き換えない。
    uncertain={'P035','P056','P057','P102','P113','P116','P118','P133'}
    sensitivity=[]
    for app in sorted(MAIN):
        group=[r for r in rich if r['appid']==app]
        baseline=sum(bool(r['comparisons']) for r in group)
        conservative=sum(bool(r['comparisons']) and r['sample_id'] not in uncertain for r in group)
        sensitivity.append(dict(appid=app,n=len(group),baseline_comparison_reviews=baseline,conservative_comparison_reviews=conservative))
    (dest/'pilot_sensitivity.json').write_text(json.dumps(sensitivity,indent=2),encoding='utf-8')
    report=['# 先導集計（未検証AIラベル）','', '正式対象は4作品、各30件、計120件。SO2Rの診断30件は主集計から除外。割合は小標本の記述であり、全量の意味分析結果ではない。','', '|作品AppID|全取得件数|推薦|非推薦|先導評価あり|先導旧版比較あり|','|---|---:|---:|---:|---:|---:|']
    for r in audit:report.append(f"|{r['appid']}|{r['n']}|{r['positive']}|{r['negative']}|{r['pilot_any_evaluation']}/30|{r['pilot_any_comparison']}/30|")
    report+=['','|AppID|要素|評価あり|正|負|混合|旧版比較|相対正|相対負|相対混合|維持|方向未評価|','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in detail:report.append('|'+ '|'.join(str(r[k]) for k in ['appid','aspect_ja','evaluated','positive','negative','mixed','compared','relative_positive','relative_negative','relative_mixed','relative_no_change','relative_unevaluated'])+'|')
    report+=['','保持への賛否はdata/pilot_labels_unvalidated.jsonのcomparison_valenceに別記。維持は改善でも退歩でもない。現在評価のみ・比較のみも別に数える。','', '根拠文字列と位置を全件機械照合したが、意味的な正しさの検証にはならない。', '', '推薦別分析と感度分析は対応JSONを参照。']
    (dest/'pilot_report_ja.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=False,indent=2))
    print('Evidence spans checked:',sum(len(v['evidence']) for r in rich for v in r['current'].values())+sum(len(r['comparisons']) for r in rich))
if __name__=='__main__': main()
