"""一次公開ページ・DOI書誌データと本研究への適用限界を記録。"""
import concurrent.futures, datetime, json, pathlib, urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
# ID, language, DOI, citation fallback, role, checked location, limit
ENTRIES=[
('J01','ja',None,'丸谷和史・横坂拓巳・磯谷悠子・大谷智子 (2024). ゲームのリメイク作品に対する評価を決定づける体験要素. エンタテインメントコンピューティングシンポジウム2024論文集, 255–260.','重制作品の体験要素と評価差','本文1–2節・5.3–5.4節','質問紙研究。レビュー中の比較出現率は検証していない。'),
('J02','ja','10.57518/digrajproc.15.0_155','丸谷和史・横坂拓巳・磯谷悠子・大谷智子 (2025). オリジナル作品との関係に基づくリメイク作品に対する評価の特徴の検討. 日本デジタルゲーム学会年次大会予稿集, 15, 155–160.','作品単体と再構成の評価を区別','本文1節・概要','二つの評価軸を本研究の二種のテキストラベルと同一視しない。負評の比較頻度は導けない。'),
('J03','ja','10.9762/digraj.4.1_69','川島隆徳・村井源・徃住彰文 (2010). ゲーム批評から見たゲームの「面白さ」―レビューテキストの計量解析による叙述対象の自動抽出―. デジタルゲーム学研究, 4(1), 69–80.','要素に着目する国内の蓄積','出版社日本語ページ・抄録。PDF取得済みだが抽出テキストの文字化けあり','雑誌批評が対象。Steamユーザーレビューと同一母集団ではない。本文全体の読解は未了。'),
('J04','ja','10.57413/wii.20.0_136','池町和史・山西良典 (2024). レビュー文に対する係り受け解析を用いたビデオゲームにおけるプレイヤの着目点の分析. Webインテリジェンスとインタラクション研究会予稿集, 20, 136–142.','要素と評価対象の結び付け','本文1–2節・概要','係り受けによる着目点分析であり旧版比較関係の精度根拠にはならない。'),
('J05','ja','10.57518/digrajproc.15.0_145','廣田雅春 (2025). Steamにおけるビデオゲームの日本語レビューのジャンルごとの感情分析. 日本デジタルゲーム学会年次大会予稿集, 15, 145–148.','Steam日本語レビュー研究','本文概要・導入','ジャンルと感情の分析。要素別極性と原作比較の二重抽出とは異なる。'),
('J06','ja','10.57518/digrajprocsummer.2025.0_9','廣田雅春・下田紀之 (2025). Steamにおけるビデオゲームの日本語レビューを用いたジャンルごとのレビュー観点に関する分析. 日本デジタルゲーム学会夏季研究発表大会予稿集, 2025, 9–14.','最も近い国内のLLM要素抽出','本文4.1節・5.3節','5.3節で定量的精度・再現率の未評価を明記。本研究でも独立検証が必要で、LLM採用だけを新規性としない。'),
('E01','en','10.1109/CoG60054.2024.10645618','Yokosaka, T., Miura, K., Isogaya, Y., Ohtani, T., & Maruya, K. (2024). Factors of player experience in describing the relationship between remade and original works. 2024 IEEE Conference on Games.','重制と原作の関係','IEEEの公開抄録・会議目次','本文取得未了。質問紙尺度の再利用は本文・尺度項目を確認後。'),
('E02','en','10.1177/15554120231163655','Brown, L. (2024). Rethinking Remakes: Value and Culture in Video Game Temporalization. Games and Culture, 19(3), 337–356.','重制・再発の文化的位置','出版社公開抄録','本文取得未了。temporalizationの詳細な類型は二次要約から引用しない。'),
('E03','en','10.5210/spir.v2020i0.11286','Neill Hoch, I. (2020). Nostalgia for the New: Video Game “Remakes” and the Limits of Reflection. AoIR Selected Papers of Internet Research.','懐旧枠組みと本研究の境界','公開本文pp.1–3','予告編YouTubeコメントの短論文。レビューの明示比較から心理的懐旧を推定しない。'),
('E04','en','10.1007/s10664-018-9627-4','Lin, D., Bezemer, C.-P., Zou, Y., & Hassan, A. E. (2019). An empirical study of game reviews on the Steam platform. Empirical Software Engineering, 24, 170–207.','Steamレビューのデータ特性','著者公開稿・抄録・方法・考察','推薦・非推薦双方の情報を扱う根拠。旧版比較が非推薦に多いという証拠ではない。'),
('E05','en',None,'Hunicke, R., LeBlanc, M., & Zubek, R. (2004). MDA: A Formal Approach to Game Design and Game Research. AAAI Workshop on Challenges in Game AI.','ゲーム設計概念と分類の区別','AAAI本文pp.1–2','Mechanics/Dynamics/Aestheticsを本研究の5分類の原典とはしない。'),
('E06','en','10.3115/v1/S14-2004','Pontiki, M., et al. (2014). SemEval-2014 Task 4: Aspect Based Sentiment Analysis. SemEval 2014, 27–35.','対象・観点・極性の分離','本文タスク定義','飲食店・ノートPCの枠組み。日本語ゲームへの性能を保証しない。'),
('E07','en','10.18653/v1/S16-1002','Pontiki, M., et al. (2016). SemEval-2016 Task 5: Aspect Based Sentiment Analysis. SemEval 2016, 19–30.','観点レベル分析の拡張','ACL書誌・本文タスク定義','多言語ABSAの設計参照。旧版比較・実装維持の専用コードが別途必要。'),
('E08','en','10.1145/1148170.1148215','Jindal, N., & Liu, B. (2006). Identifying comparative sentences in text documents. SIGIR 2006, 244–251.','比較文の検出','著者公開稿・導入','検出と方向判定を分ける。英語の比較語リストを日本語へそのまま適用しない。'),
('E09','en',None,'Jindal, N., & Liu, B. (2006). Mining Comparative Sentences and Relations. AAAI 2006, 1331–1336.','比較対象・特徴・関係のタプル','AAAI本文p.1331・関係定義','客観的比較も存在するため、比較の存在を肯定・否定と同一視しない。E08とは別論文だが同系統。'),
('E10','en','10.1073/pnas.2305016120','Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. PNAS, 120(30), e2305016120.','LLMによる注釈の可能性','PNAS公開抄録・著者プレプリント','最終版と初期arXivで標本数が違う。日本語の複合比較タスクへ外挿しない。'),
('E11','en','10.6092/issn.1971-8853/19461','Törnberg, P. (2024). Best Practices for Text Annotation with Large Language Models. Sociologica, 18(2), 67–85.','固定仕様・独立検証・安定性','出版本文6節・9節','プロンプト確定後の検証が必要。本先導データは精度評価に流用しない。'),
('E12','en','10.1177/1609406919899220','O’Connor, C., & Joffe, H. (2020). Intercoder Reliability in Qualitative Research: Debates and Practical Guidelines. International Journal of Qualitative Methods, 19.','人手コード化の透明性','出版社抄録・導入','一致率だけで解釈妥当性を保証しない。相違の協議過程も報告する。'),
('E13','en','10.1093/pan/mps028','Grimmer, J., & Stewart, B. M. (2013). Text as Data: The Promise and Pitfalls of Automatic Content Analysis Methods for Political Texts. Political Analysis, 21(3), 267–297.','自動テキスト測定の妥当性','公開本文概要・導入','文脈固有の検証が必要。自動化自体は内容上の貢献を保証しない。'),
('E14','en','10.1080/0267257X.2025.2520859','Butcher, L., & Toh, A. (2025). Strolling down memory card lane: nostalgia, age, and video game remakes. Journal of Marketing Management, 41(9–10), 892–909.','懐旧・購買意図との境界','出版社公開抄録・導入','質問紙研究。本文の明示比較は懐旧尺度や購買意図を代替しない。'),
]
URLS={'J01':'https://ipsj.ixsq.nii.ac.jp/records/238728','E05':'https://aaai.org/papers/ws04-04-001-mda-a-formal-approach-to-game-design-and-game-research/','E09':'https://cdn.aaai.org/AAAI/2006/AAAI06-209.pdf'}
def retrieve(row):
    key,lang,doi,citation,role,checked,limit=row
    out=dict(id=key,language=lang,doi=doi,citation=citation,url=('https://doi.org/'+doi) if doi else URLS[key],role_ja=role,checked_ja=checked,limit_ja=limit,access_date_jst='2026-10-27')
    if doi:
        try:
            with urllib.request.urlopen('https://api.crossref.org/works/'+doi,timeout=25) as r: meta=json.load(r)['message']
            out['crossref']={k:meta.get(k) for k in ['title','author','container-title','published','volume','issue','page','type','DOI']}
            out['metadata_status']='DOI metadata retrieved'
        except Exception as e:out['metadata_status']='publisher page verified; Crossref retrieval failed: '+str(e)
    else:out['metadata_status']='publisher/source page verified'
    return out
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: rows=list(pool.map(retrieve,ENTRIES))
    dest=ROOT/'literature';dest.mkdir(exist_ok=True)
    (dest/'references.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    md=['# 参考文献・適用範囲の照合台帳','', '日本語6編・英語14編、計20編。学位論文や翻訳ページを日本語論文数に算入しない。抄録のみ確認した文献と本文確認済みの文献を区別する。元の10編の一覧は現チャットに存在せず、維持できたとは未確認。全文PDFは著作権を一律に再許諾できないため公開しない。','']
    for r in rows:md += [f"## {r['id']} [{r['citation']}]({r['url']})",'',f"- 言語：{r['language']}。用途：{r['role_ja']}。",f"- 照合箇所：{r['checked_ja']}。",f"- 適用限界：{r['limit_ja']}",'']
    (dest/'references_ja.md').write_text('\n'.join(md),encoding='utf-8')
    print('references',len(rows),'Japanese',sum(r['language']=='ja' for r in rows))
