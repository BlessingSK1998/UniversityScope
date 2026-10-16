"""Build static charts that render on GitHub, from the same cleaned snapshot."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import LogNorm
from analytics import FEATURES, METRICS, cluster_profiles, quality_report
from pipeline import load_data, clean
from geography import country_codes

BG, PANEL, TEXT, MUTED, CYAN, PURPLE = '#0a1020','#111d32','#e6edf9','#a5b8d4','#58d9c9','#a393fa'
LABELS = ['Teaching','Research','Citations','Industry income','International outlook']

def split_dateline(ring):
    """Unwrap longitudes then clip at the antimeridian in this equirectangular view."""
    if not ring:return []
    unwrapped=[ring[0]]
    for x,y in ring[1:]:
        while x-unwrapped[-1][0]>180:x-=360
        while x-unwrapped[-1][0]<-180:x+=360
        unwrapped.append((x,y))
    def clip(points,bound,greater):
        out=[]
        if not points:return out
        previous=points[-1]
        for current in points:
            before=previous[0]>=bound if greater else previous[0]<=bound
            inside=current[0]>=bound if greater else current[0]<=bound
            if inside!=before:
                t=(bound-previous[0])/(current[0]-previous[0])
                out.append((bound,previous[1]+t*(current[1]-previous[1])))
            if inside:out.append(current)
            previous=current
        return out
    result=[]
    for shift in [-720,-360,0,360,720]:
        points=[(x+shift,y) for x,y in unwrapped]
        points=clip(clip(points,-180,True),180,False)
        if len(points)>=3:result.append(points)
    return result

def country_rings(world):
    """Decode published TopoJSON delta arcs; never invent geographic outlines."""
    scale = world['transform']['scale']; translate = world['transform']['translate']
    arcs=[]
    for arc in world['arcs']:
        x=y=0; points=[]
        for dx,dy in arc:
            x+=dx; y+=dy
            points.append((x*scale[0]+translate[0], y*scale[1]+translate[1]))
        arcs.append(points)
    for geometry in world['objects']['countries']['geometries']:
        polygons = [geometry['arcs']] if geometry['type']=='Polygon' else geometry['arcs']
        for polygon in polygons:
            # Exterior rings are adequate at this overview scale; holes are not filled separately.
            ring=[]
            for ref in polygon[0]:
                points=arcs[ref] if ref>=0 else list(reversed(arcs[~ref]))
                ring.extend(points if not ring else points[1:])
            for part in split_dateline(ring):
                yield str(int(geometry['id'])) if geometry.get('id') else 'unknown', part

def generate_visuals(df, provenance, raw=None, output_dir='assets'):
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'figure.facecolor':BG,'axes.facecolor':BG,'axes.edgecolor':'#30415e','text.color':TEXT,'axes.labelcolor':MUTED,'xtick.color':MUTED,'ytick.color':MUTED,'grid.color':'#25334a','svg.fonttype':'none','savefig.facecolor':BG})
    ranked=df.loc[df.academic_status.eq('Ranked')]
    complete,scores,profiles,best=cluster_profiles(df)
    df=df.copy();df['cluster']=pd.Series(pd.NA,index=df.index,dtype='Int64')
    if best is not None:df.loc[complete.index,'cluster']=complete['cluster']
    artifacts=[]
    def finish(fig,name,title,subtitle):
        fig.suptitle(title,x=0.055,y=0.98,ha='left',fontsize=21,fontweight='bold',color=TEXT)
        fig.text(0.055,0.90,subtitle,fontsize=10,color=MUTED)
        fig.text(0.055,0.025,'UniversityScope  |  Blessing Sekeramavi  |  Source: Times Higher Education; edition unverified',fontsize=8,color=MUTED)
        fig.subplots_adjust(top=0.82,bottom=0.14,left=0.12,right=0.94)
        fig.savefig(output_dir/(name+'.svg'))
        fig.savefig(output_dir/(name+'.png'),dpi=150)
        plt.close(fig);artifacts.append(name)
    # Country coverage from published boundary geometry.
    world=json.loads((Path(__file__).parent/'assets/world-countries.json').read_text())
    codes=country_codes(df.location.unique())
    counts={}
    for name,n in ranked.location.value_counts().items():
        code=codes[name]
        if code:
            key=str(int(code['numeric']));counts[key]=counts.get(key,0)+int(n)
    fig,ax=plt.subplots(figsize=(13,7))
    polygons=[];values=[];visible=set()
    for country,ring in country_rings(world):
        if ring:
            polygons.append(Polygon(ring,closed=True));values.append(counts.get(country,0));visible.add(country)
    collection=PatchCollection(polygons,cmap='viridis',edgecolor='#52617a',linewidth=0.25,norm=LogNorm(vmin=1,vmax=max(2,max(counts.values(),default=1))))
    collection.set_array(np.ma.masked_equal(np.array(values),0));collection.cmap.set_bad('#17243b');ax.add_collection(collection)
    ax.set_xlim(-180,180);ax.set_ylim(-60,85);ax.set_aspect('equal');ax.axis('off')
    bar=fig.colorbar(collection,ax=ax,orientation='horizontal',fraction=0.045,pad=0.05,shrink=0.55);bar.set_label('Ranked institutions per country (logarithmic colour scale)')
    represented=sum(n for key,n in counts.items() if key in visible)
    finish(fig,'world-coverage','A global view of university coverage',f'{len(ranked):,} ranked institutions · {represented:,} represented in low-resolution country geometry · equirectangular overview')
    fig,ax=plt.subplots(figsize=(12,7));top=ranked.location.value_counts().head(12).sort_values();ax.barh(top.index,top.values,color=CYAN,height=0.65);ax.bar_label(ax.containers[0],padding=6,color=TEXT);ax.set_xlim(0,float(top.max())*1.17 if len(top) else 1);ax.set_xlabel('Ranked institutions');ax.grid(axis='x',alpha=0.4);ax.set_axisbelow(True);fig.subplots_adjust(left=0.24)
    if not len(top):ax.text(.5,.5,'No ranked records',transform=ax.transAxes,ha='center')
    finish(fig,'country-coverage','Where ranked institutions are represented',f'Top 12 countries / territories · {int(top.sum()):,} of {len(ranked):,} ranked institutions');
    # Scatter: full axis scale and zero/missing distinction.
    fig,ax=plt.subplots(figsize=(12,7));valid=ranked.dropna(subset=['score_teaching_lower','score_research_lower']);ax.scatter(valid.score_teaching_lower,valid.score_research_lower,s=17,alpha=0.4,color=CYAN,edgecolors='none',rasterized=False);ax.set(xlim=(0,100),ylim=(0,100),xlabel='Teaching score (lower bound)',ylabel='Research score (lower bound)');ax.grid(alpha=0.25);ax.set_axisbelow(True);r=valid.score_teaching_lower.corr(valid.score_research_lower);ax.text(0.98,0.04,f'Pearson r = {r:.2f}' if pd.notna(r) else 'Pearson r unavailable',transform=ax.transAxes,ha='right',color=TEXT)
    finish(fig,'teaching-research','Teaching and research score profiles',f'{len(valid):,} complete ranked records · association does not establish causation')
    fig,ax=plt.subplots(figsize=(12,7));corr=ranked[FEATURES].corr();image=ax.imshow(corr,vmin=-1,vmax=1,cmap='coolwarm',aspect='auto');ax.set_xticks(range(5),['Teaching','Research','Citations','Industry','Intl outlook']);ax.set_yticks(range(5),LABELS)
    for i in range(5):
        for j in range(5):ax.text(j,i,f'{corr.iloc[i,j]:.2f}' if pd.notna(corr.iloc[i,j]) else '—',ha='center',va='center',color='#07101e',fontweight='bold')
    fig.colorbar(image,ax=ax,fraction=0.045,pad=0.04,label='Pearson correlation')
    finish(fig,'score-correlations','How performance dimensions relate',f'Ranked cohort · pairwise complete observations · lower score bounds')
    fig,axes=plt.subplots(1,2,figsize=(13,7),gridspec_kw={'width_ratios':[1,1.45]});status=df.academic_status.value_counts();axes[0].bar(status.index,status.values,color=[CYAN,PURPLE,'#f4b77c','#7f9ac0'][:len(status)]);axes[0].bar_label(axes[0].containers[0],padding=4,color=TEXT);axes[0].set_ylabel('Institutions');axes[0].tick_params(axis='x',rotation=20);axes[0].set_ylim(0,status.max()*1.2)
    groups=[name for name in ['Ranked','Reporter','Disabled','Unknown/unranked'] if name in set(df.academic_status)];missing=df.groupby('academic_status')[FEATURES].agg(lambda s:s.isna().mean()*100).loc[groups];im=axes[1].imshow(missing,vmin=0,vmax=100,cmap='magma');axes[1].set_xticks(range(5),['Teaching','Research','Citations','Industry','Intl outlook'],rotation=25,ha='right');axes[1].set_yticks(range(len(groups)),groups)
    for i in range(len(groups)):
        for j in range(5):axes[1].text(j,i,f'{missing.iloc[i,j]:.0f}%',ha='center',va='center',color='#fff' if missing.iloc[i,j]<60 else '#111')
    axes[0].set_title('Source record classification',loc='left',color=MUTED);axes[1].set_title('Missing score fields by status',loc='left',color=MUTED);fig.subplots_adjust(wspace=0.45)
    finish(fig,'data-quality','Coverage starts with data quality',f'{len(df):,} records preserved · missing scores remain missing · status uses source rank and disabled flag')
    fig,axes=plt.subplots(1,2,figsize=(13,7),gridspec_kw={'width_ratios':[1,1.6]});
    if best is not None:
        ordered=scores.sort_values('k');axes[0].plot(ordered.k,ordered.silhouette,marker='o',color=CYAN,linewidth=2);axes[0].set_xticks(ordered.k);axes[0].set(xlabel='Number of clusters (K)',ylabel='Silhouette score');axes[0].grid(alpha=0.25)
        width=0.8/len(profiles)
        for n,(cluster,row) in enumerate(profiles.iterrows()):axes[1].bar(np.arange(5)-0.4+width/2+n*width,row.values,width,label=f'Cluster {cluster}',color=[CYAN,PURPLE,'#f4b77c','#7f9ac0','#ee91af'][n])
        axes[1].set_xticks(range(5),['Teaching','Research','Citations','Industry','Intl outlook'],rotation=20);axes[1].set_ylim(0,100);axes[1].set_ylabel('Mean lower score bound');axes[1].legend(frameon=False,labelcolor=TEXT);axes[1].grid(axis='y',alpha=0.25);axes[1].set_axisbelow(True)
    else:
        for ax in axes:ax.text(.5,.5,'Insufficient distinct complete profiles',transform=ax.transAxes,ha='center')
    fig.subplots_adjust(wspace=0.3)
    finish(fig,'cluster-profiles','Exploratory groups in performance scores',f'{len(complete):,} complete ranked records · selected K={best} by silhouette · descriptive groups, not institutional missions')
    report=quality_report(raw if raw is not None else df,df);report.update({'provenance':provenance,'best_k':best,'clustering_complete_cases':len(complete),'silhouette_scores':scores.to_dict(orient='records'),'visuals':artifacts})
    report['unresolved_country_names']=[name for name,code in codes.items() if code is None]
    report['ranked_records_in_geometry']=represented
    (output_dir/'analysis-summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return df, report

if __name__=='__main__':
    raw,provenance=load_data();df,report=generate_visuals(clean(raw),provenance,raw)
    from dashboard import build_dashboard
    build_dashboard(df,provenance)
    print(json.dumps({'records':report['records'],'visuals':report['visuals'],'dashboard':'universityscope_dashboard.html'},indent=2))
