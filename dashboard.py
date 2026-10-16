"""Generate a standalone dashboard and embed it directly in Colab/Jupyter."""
from pathlib import Path
import json
import html
import pandas as pd
from geography import country_codes

def build_dashboard(df, provenance, template=None, output='universityscope_dashboard.html', world_path=None):
    countries = country_codes(df['location'].unique())
    root = Path(__file__).resolve().parent
    template = Path(template) if template else root / 'dashboard.html'
    world_path = Path(world_path) if world_path else root / 'assets/world-countries.json'
    columns = ['name', 'location', 'rank_original', 'rank_lower_bound', 'academic_status']
    if 'cluster' in df:
        columns.append('cluster')
    columns += [c for c in df if c.startswith('score_') and (c.endswith('_lower') or c.endswith('_upper'))]
    data = json.loads(df[columns].to_json(orient='records'))
    world = json.loads(world_path.read_text(encoding='utf-8'))
    payload = json.dumps({'rows': data, 'countries': countries, 'provenance': provenance, 'world':world}, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c')
    document = template.read_text(encoding='utf-8').replace('__PAYLOAD__', payload)
    Path(output).write_text(document, encoding='utf-8')
    return document

def show_dashboard(document, height=1050):
    from IPython.display import HTML, display
    display(HTML('<iframe title="UniversityScope interactive dashboard" style="width:100%;height:' + str(height) + 'px;border:0;border-radius:16px" sandbox="allow-scripts allow-same-origin allow-downloads" srcdoc="' + html.escape(document, quote=True) + '"></iframe>'))
