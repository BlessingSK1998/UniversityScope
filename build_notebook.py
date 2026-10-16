"""Generate the portable notebook from canonical source files and optional real results."""
from pathlib import Path
import argparse
import base64
import json

ROOT=Path(__file__).resolve().parent
SOURCES=['pipeline.py','geography.py','analytics.py','visuals.py','dashboard.py','dashboard.html','assets/world-countries.json']
def markdown(text):return {'cell_type':'markdown','metadata':{},'source':text.splitlines(True)}
def code(text):return {'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':text.splitlines(True)}

def build(with_results=False):
    files={name:(ROOT/name).read_text(encoding='utf-8') for name in SOURCES}
    cells=[markdown('''# UniversityScope
**Global university performance and geographic exploration**  
Blessing Sekeramavi · Data science and international outreach

**In Colab: Runtime → Run all.** The interactive dashboard appears in the final cell. Static charts below also display in GitHub. Upload `times_higher_education_rankings.csv` through Colab's Files sidebar to reuse a saved snapshot. Without it, source retrieval is attempted.

Maps show country aggregates, not campus locations. Score charts use lower bounds when the publisher reports intervals. Missing values remain missing. The source uses a `latest` URL, so the ranking edition must be verified separately.
'''),code('''%pip -q install "pandas>=2.2,<3" "numpy>=1.26,<3" "requests>=2.31,<3" "beautifulsoup4>=4.12,<5" "pycountry>=24.6" "matplotlib>=3.8,<4" "scikit-learn>=1.4,<2"
'''),markdown('''## 1. Prepare the project
This portable notebook contains the same helper files and world boundaries as the repository. `build_notebook.py` regenerates these cells when the canonical source changes. No separate clone or source download is needed.
'''),code('''from pathlib import Path
import json
import importlib
from IPython.display import display, Image

project_files = '''+repr(files)+'''
for name, content in project_files.items():
    target=Path(name)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(content,encoding='utf-8')
for module in ['pipeline','geography','analytics','dashboard','visuals']:
    importlib.reload(importlib.import_module(module))
print('Project helpers and world boundaries ready.')
'''),markdown('''## 2. Load, validate and analyze
The CSV is reused if present. A network or source-layout failure asks for your saved CSV. Cleaning retains interval bounds, flags invalid score fields and preserves every record. Clustering uses complete ranked component scores and selects K by silhouette among the tested candidates. Complete-case selection, scaling and the ranking framework limit interpretation.
'''),code('''from pipeline import load_data, clean
from visuals import generate_visuals
raw, provenance=load_data()
df=clean(raw)
df, report=generate_visuals(df,provenance,raw)
df.to_csv('times_higher_education_cleaned.csv',index=False)
print(f"{report['records']:,} records across {report['locations']:,} locations")
print(json.dumps(report['statuses'],indent=2))
print(f"Best tested K: {report['best_k']} · complete clustering records: {report['clustering_complete_cases']:,}")
print(provenance)
'''),markdown('''## 3. Visual report
All charts are calculated from the snapshot used above. These images also render on GitHub. Country map colours use a logarithmic count scale; other chart axes show their explicit units. Correlations describe associations, not causal effects. Cluster numbers are neutral fitted labels, not institutional missions.
'''),code('''for name in report['visuals']:
    display(Image(filename=f'assets/{name}.png'))
'''),markdown('''## 4. Interactive dashboard and maps
Explore the 3D globe or 2D map, search and filter institutions, compare up to four universities and export a shortlist. Cluster profiles use fitted full-cohort labels; filtering changes displayed members, not the fitted model.

The dashboard appears in the frame below. Scroll inside it for comparisons and the institution table. JavaScript libraries need CDN access. If WebGL fails, the 2D map is used. Country boundaries are embedded. Low-resolution geometry omits some small territories; coverage is reported separately from country-code matches.

Download `universityscope_dashboard.html` from Colab's Files sidebar to open it in a browser. GitHub notebook previews do not execute interactive JavaScript.
'''),code('''from dashboard import build_dashboard, show_dashboard
document=build_dashboard(df,provenance)
show_dashboard(document,height=1150)
print('Dashboard displayed above. Standalone file: universityscope_dashboard.html')
''')]
    for i,cell in enumerate(cells):cell['id']=f'universityscope-{i:02d}'
    if with_results:
        summary=json.loads((ROOT/'assets/analysis-summary.json').read_text())
        cells[5]['outputs']=[{'output_type':'stream','name':'stdout','text':[f"Saved validation snapshot: {summary['records']:,} records across {summary['locations']:,} locations. Best tested K={summary['best_k']}.\n",summary['provenance']+'\n']}]
        cells[7]['outputs']=[{'output_type':'display_data','metadata':{},'data':{'image/png':base64.b64encode((ROOT/'assets'/f'{name}.png').read_bytes()).decode(),'text/plain':f'Calculated visual: {name}'}} for name in summary['visuals']]
    return {'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'},'colab':{'name':'UniversityScope.ipynb','provenance':[]}},'cells':cells}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--with-results',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args();nb=build(args.with_results)
    if args.check:
        existing=json.loads((ROOT/'UniversityScope.ipynb').read_text())
        assert [(c['cell_type'],c['source']) for c in nb['cells']]==[(c['cell_type'],c['source']) for c in existing['cells']], 'Notebook source drift: run python build_notebook.py --with-results'
        print('Notebook source matches canonical modules.')
    else:(ROOT/'UniversityScope.ipynb').write_text(json.dumps(nb,indent=1),encoding='utf-8')
