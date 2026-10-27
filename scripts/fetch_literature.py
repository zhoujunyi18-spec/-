"""公開全文を取得し、本文照合用テキストと取得記録をローカルに保存する。"""
import datetime, hashlib, json, pathlib, urllib.request
from pypdf import PdfReader
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCES={
'J01':'https://ipsj.ixsq.nii.ac.jp/record/238728/files/IPSJ-EC2024039.pdf',
'J02':'https://www.jstage.jst.go.jp/article/digrajproc/15/0/15_155/_pdf/-char/ja',
'J03':'https://www.jstage.jst.go.jp/article/digraj/4/1/4_69/_pdf',
'J04':'https://www.jstage.jst.go.jp/article/wii/20/0/20_136/_pdf/-char/ja',
'J05':'https://www.jstage.jst.go.jp/article/digrajproc/15/0/15_145/_pdf/-char/ja',
'J06':'https://www.jstage.jst.go.jp/article/digrajprocsummer/2025/0/2025_9/_pdf/-char/ja',
'E03':'https://spir.aoir.org/ojs/index.php/spir/article/download/11286/9958/72213',
'E04':'https://sail.cs.queensu.ca/data/pdfs/EMSE2018_AnEmpiricalStudyOfGameReviewsOnTheSteamPlatform.pdf',
'E05':'https://cdn.aaai.org/Workshops/2004/WS-04-04/WS04-04-001.pdf',
'E06':'https://aclanthology.org/S14-2004.pdf',
'E07':'https://aclanthology.org/S16-1002.pdf',
'E08':'https://www.cs.uic.edu/~liub/publications/sigir06-comp.pdf',
'E09':'https://cdn.aaai.org/AAAI/2006/AAAI06-209.pdf',
'E10':'https://arxiv.org/pdf/2303.15056',
'E11':'https://arxiv.org/pdf/2402.05129',
'E12':'https://journals.sagepub.com/doi/pdf/10.1177/1609406919899220',
'E13':'https://www.cambridge.org/core/services/aop-cambridge-core/content/view/F7AAC8B2909441603FEB25C156448F20/S1047198700013401a.pdf/text-as-data-the-promise-and-pitfalls-of-automatic-content-analysis-methods-for-political-texts.pdf',
'E14':'https://www.tandfonline.com/doi/pdf/10.1080/0267257X.2025.2520859',
}
if __name__=='__main__':
    dest=ROOT/'literature'/'fulltext'; dest.mkdir(parents=True,exist_ok=True)
    log=[]
    for key,url in SOURCES.items():
        item=dict(id=key,url=url,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        try:
            cache=dest/f'{key}.pdf'
            if cache.exists(): body=cache.read_bytes()
            else:
                with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=35) as r: body=r.read()
            if not body.startswith(b'%PDF'): raise ValueError('Response is not a PDF')
            target=dest/f'{key}.pdf'; target.write_bytes(body)
            pdf=PdfReader(target)
            (dest/f'{key}.txt').write_text('\n\n'.join(f'--- PDF page {i+1} ---\n'+(p.extract_text() or '') for i,p in enumerate(pdf.pages)),encoding='utf-8')
            item.update(status='downloaded',pages=len(pdf.pages),sha256=hashlib.sha256(body).hexdigest())
        except Exception as e: item.update(status='failed',error=str(e))
        log.append(item); print(key,item['status'],flush=True)
    (ROOT/'literature'/'retrieval_log.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
