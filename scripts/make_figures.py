"""公式API監査値・未検証先導値を混同せず図示する。"""
import csv,json,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
ROOT=pathlib.Path(__file__).resolve().parents[1]
for font in ['C:/Windows/Fonts/YuGothR.ttc','C:/Windows/Fonts/msgothic.ttc','C:/Windows/Fonts/msyh.ttc']:
    if pathlib.Path(font).exists():
        font_manager.fontManager.addfont(font);plt.rcParams['font.family']=font_manager.FontProperties(fname=font).get_name();break
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.unicode_minus':False})
NAMES={2455640:'ロマサガ2',2701660:'DQIII',2161700:'P3R',3375780:'空の軌跡 the 1st'}
def main():
    out=ROOT/'figures';out.mkdir(exist_ok=True)
    audit=json.loads((ROOT/'results/main_data_audit.json').read_text(encoding='utf-8'))
    by={r['appid']:r for r in audit};order=list(NAMES)
    fig,ax=plt.subplots(figsize=(9,4.6),layout='constrained')
    for i,a in enumerate(order):
        r=by[a];p=r['positive']/r['n']*100
        ax.barh(i,p,color='#327896',label='推薦' if i==0 else None)
        ax.barh(i,100-p,left=p,color='#c27955',label='非推薦' if i==0 else None)
        ax.text(p/2,i,f"{r['positive']:,}",va='center',ha='center',color='white')
        if 100-p>5:ax.text(p+(100-p)/2,i,str(r['negative']),va='center',ha='center',color='white')
        ax.text(101,i,f"N={r['n']:,} / 非推薦 {r['negative']}",va='center',fontsize=9)
    ax.set(yticks=range(4),yticklabels=[NAMES[a] for a in order],xlim=(0,132),xlabel='取得レビューに占める割合（%）',title='データ監査：推薦フラグの分布（本文の極性ではない）');ax.invert_yaxis();ax.set_xticks([0,25,50,75,100]);ax.legend(loc='upper center',bbox_to_anchor=(0.5,-0.17),ncol=2,frameon=False)
    fig.savefig(out/'01_corpus_recommendation.png',dpi=180);fig.savefig(out/'01_corpus_recommendation.svg');plt.close(fig)
    rows=list(csv.DictReader((ROOT/'results/pilot_aspects.csv').open(encoding='utf-8-sig')))
    aspects=['B','E','N','U','A'];labels=['戦闘・成長','探索・誘導','物語・人物','UI・操作','視聴覚']
    matrix=[[int(next(r for r in rows if int(r['appid'])==a and r['aspect']==b)['evaluated']) for b in aspects] for a in order]
    fig,ax=plt.subplots(figsize=(8,4.5),layout='constrained');im=ax.imshow(matrix,cmap='Blues',vmin=0,vmax=30)
    for i,line in enumerate(matrix):
        for j,n in enumerate(line):ax.text(j,i,f'{n}/30',ha='center',va='center',color='white' if n>15 else '#203040')
    ax.set(xticks=range(5),xticklabels=labels,yticks=range(4),yticklabels=[NAMES[a] for a in order],title='AI先導標本：現在評価の被覆件数（未検証）');fig.colorbar(im,ax=ax,label='レビュー数（各作品30件）')
    fig.savefig(out/'02_pilot_coverage_unvalidated.png',dpi=180);fig.savefig(out/'02_pilot_coverage_unvalidated.svg');plt.close(fig)
    print('2 figures generated')
if __name__=='__main__':main()
