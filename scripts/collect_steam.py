"""Steam公式APIから日本語レビューを取得する。Python標準ライブラリのみ。"""
import argparse, datetime as dt, hashlib, json, pathlib, time, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
APPS = {2455640: 'ロマンシング サガ2 リベンジオブザセブン', 2701660: 'ドラゴンクエストIII HD-2D Remake', 2161700: 'ペルソナ3 リロード', 3375780: '空の軌跡 the 1st'}
END = int(dt.datetime(2026,10,26,23,59,59,tzinfo=dt.timezone(dt.timedelta(hours=9))).timestamp())
API = 'https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/'

def fetch(params):
    url = API + '?' + urllib.parse.urlencode({'input_json': json.dumps(params)})
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'JRPG-Remake-Research/0.1'})
            with urllib.request.urlopen(req,timeout=45) as response:
                body = response.read()
                return json.loads(body)['response'], body, url
        except Exception:
            if attempt == 4: raise
            time.sleep(2 ** (attempt+1))

def collect(appid):
    dest=ROOT/'data'/'private'/str(appid); dest.mkdir(parents=True,exist_ok=True)
    records={}; cursor='*'; seen=set(); pages=[]; first=None; duplicates=0
    for page in range(1000):
        params=dict(appid=appid,filter=1,languages=['japanese'],purchase_type=1,review_type=0,num_per_page=100,filter_offtopic_activity=False,cursor=cursor,date_range_start=1,date_range_end=END)
        data,body,url=fetch(params)
        (dest/f'page_{page:04d}.json').write_bytes(body)
        if first is None: first=data
        batch=data.get('reviews',[])
        pages.append(dict(page=page,n=len(batch),sha256=hashlib.sha256(body).hexdigest(),url=url,at=dt.datetime.now(dt.timezone.utc).isoformat()))
        for r in batch:
            key=str(r['recommendationid']); duplicates+=key in records
            if r.get('language')!='japanese' or r['timestamp_created']>END: raise ValueError('Filter violation')
            r['appid']=appid; records[key]=r
        nxt=data.get('cursor')
        print(f'{appid} page={page} unique={len(records)}',flush=True)
        if not batch: stop='empty_page'; break
        if not nxt or nxt==cursor or nxt in seen: stop='cursor_stalled'; break
        seen.add(cursor); cursor=nxt
        time.sleep(0.8)
    else: stop='safety_limit'
    ordered=sorted(records.values(),key=lambda r:(r['timestamp_created'],r['recommendationid']))
    (dest/'reviews.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in ordered),encoding='utf-8')
    summary=dict(appid=appid,title=APPS[appid],cutoff_unix=END,cutoff_jst='2026-10-26T23:59:59+09:00',n=len(ordered),positive=sum(r.get('voted_up',False) for r in ordered),negative=sum(not r.get('voted_up',False) for r in ordered),duplicates=duplicates,stop=stop,api_summary=first.get('query_summary'),api_total_matching=first.get('total_matching'),pages=pages)
    (dest/'manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    return {k:v for k,v in summary.items() if k!='pages'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--appid',type=int); args=parser.parse_args()
    fresh=[collect(appid) for appid in ([args.appid] if args.appid else APPS)]
    reports=[]
    for appid in APPS:
        path=ROOT/f'data/private/{appid}/manifest.json'
        if path.exists(): reports.append({k:v for k,v in json.loads(path.read_text(encoding='utf-8')).items() if k!='pages'})
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results'/'data_audit.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
