"""Generate a standalone dashboard and embed it directly in Colab/Jupyter."""
from pathlib import Path
import json
import html
import pandas as pd

def build_dashboard(df, provenance, template='dashboard.html', output='universityscope_dashboard.html'):
    import pycountry
    aliases = {'United States': 'USA', 'United Kingdom': 'GBR', 'South Korea': 'KOR', 'Russia': 'RUS', 'Taiwan': 'TWN', 'Hong Kong': 'HKG', 'Iran': 'IRN', 'Vietnam': 'VNM', 'Türkiye': 'TUR', 'Kosovo': None}
    countries = {}
    for name in df['location'].unique():
        try:
            country = pycountry.countries.get(alpha_3=aliases[name]) if name in aliases else pycountry.countries.lookup(name)
            countries[name] = {'iso': country.alpha_3, 'numeric': country.numeric} if country else None
        except LookupError:
            countries[name] = None
    columns = ['name', 'location', 'rank_original', 'rank_lower_bound', 'academic_status']
    columns += [c for c in df if c.startswith('score_') and (c.endswith('_lower') or c.endswith('_upper'))]
    data = json.loads(df[columns].to_json(orient='records'))
    payload = json.dumps({'rows': data, 'countries': countries, 'provenance': provenance}, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c')
    document = Path(template).read_text().replace('__PAYLOAD__', payload)
    Path(output).write_text(document)
    return document

def show_dashboard(document, height=1050):
    from IPython.display import HTML, display
    display(HTML('<iframe title="UniversityScope interactive dashboard" style="width:100%;height:' + str(height) + 'px;border:0;border-radius:16px" sandbox="allow-scripts allow-same-origin allow-downloads" srcdoc="' + html.escape(document, quote=True) + '"></iframe>'))
