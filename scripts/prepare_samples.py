"""固定ハッシュ順による先導標本と非重複の人手検証標本を作成。"""
import csv, hashlib, json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def rank(r,phase):
    return hashlib.sha256(f'20261027:{phase}:{r["appid"]}:{r["recommendationid"]}'.encode()).hexdigest()
def main():
    rows=[]
    for p in sorted((ROOT/'data'/'private').glob('*/reviews.jsonl')):
        if int(p.parent.name) not in {2161700,2238900,2455640,2701660,3375780}:continue
        rows.extend(json.loads(line) for line in p.read_text(encoding='utf-8').splitlines())
    pilot=[]; holdout=[]
    for a in sorted({r['appid'] for r in rows}):
        pool=[r for r in rows if r['appid']==a]
        selected=sorted(pool,key=lambda r:rank(r,'pilot'))[:30]
        selected_ids={r['recommendationid'] for r in selected}
        rest=[r for r in pool if r['recommendationid'] not in selected_ids]
        pilot.extend(selected)
        if a!=2238900:
            holdout.extend(sorted(rest,key=lambda r:rank(r,'validation'))[:50])
    for phase,sample in [('pilot',pilot),('validation',holdout)]:
        dest=ROOT/'data'/'private'/phase; dest.mkdir(exist_ok=True)
        out=[]
        for i,r in enumerate(sample,1):
            out.append(dict(sample_id=f'{phase[:1].upper()}{i:03}',appid=r['appid'],recommendationid=r['recommendationid'],review=r['review'],voted_up=r.get('voted_up',False),timestamp_created=r['timestamp_created']))
        (dest/'sample.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in out),encoding='utf-8')
        if phase=='validation':
            with (dest/'blind_annotation.csv').open('w',encoding='utf-8-sig',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=['sample_id','appid','review','aspect_codes','current_polarity','comparison','reference_version','relative_polarity','evidence','notes']); writer.writeheader()
                for r in out: writer.writerow({k:r[k] for k in ['sample_id','appid','review']})
    public=ROOT/'data'/'sample_manifest.json'
    public.write_text(json.dumps(dict(seed='20261027',method='SHA256(seed:phase:appid:recommendationid) ascending; without replacement',pilot_per_game=30,main_appids=[2161700,2455640,2701660,3375780],excluded_diagnostic_appid=2238900,validation_per_game=50,disjoint=True,pilot_ids=[r['recommendationid'] for r in pilot],validation_ids=[r['recommendationid'] for r in holdout]),indent=2),encoding='utf-8')
    print('pilot',len(pilot),'validation',len(holdout),'pilot chars',sum(len(r['review']) for r in pilot))
if __name__=='__main__': main()
