"""UniversityScope: source loading and conservative numeric parsing."""
from pathlib import Path
import json
import re
import pandas as pd

SOURCE = 'https://www.timeshighereducation.com/world-university-rankings/latest/world-ranking'

def bounds(value):
    if pd.isna(value):
        return None, None
    text = str(value).strip().lstrip('=')
    if re.fullmatch(r'\d+(?:\.\d+)?', text):
        return float(text), float(text)
    match = re.fullmatch(r'(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)', text)
    if match:
        low, high = map(float, match.groups())
        return (low, high) if low <= high else (None, None)
    if re.fullmatch(r'\d+\s*\+', text):
        return float(text.rstrip('+').strip()), None
    return None, None

def clean(raw):
    required = {'name', 'location', 'rank'}
    if not required.issubset(raw.columns):
        raise ValueError(f'Missing columns: {required - set(raw.columns)}')
    df = raw.copy().reset_index(drop=True)
    df['name'] = df['name'].fillna('Unnamed institution').astype(str).str.strip()
    df['location'] = df['location'].fillna('Unknown').astype(str).str.strip()
    df['rank_original'] = df['rank'].fillna('Unknown').astype(str)
    pairs = df['rank'].apply(bounds)
    df['rank_lower_bound'] = [p[0] for p in pairs]
    df['rank_upper_bound'] = [p[1] for p in pairs]
    disabled = df.get('disabled', pd.Series(False, index=df.index)).astype(str).str.lower().isin(['true', '1'])
    df['academic_status'] = 'Unknown/unranked'
    df.loc[df['rank_lower_bound'].notna(), 'academic_status'] = 'Ranked'
    df.loc[df['rank_original'].str.contains('reporter', case=False), 'academic_status'] = 'Reporter'
    df.loc[disabled, 'academic_status'] = 'Disabled'
    for key in ['overall', 'teaching', 'research', 'citations', 'industry_income', 'international_outlook']:
        parsed = df.get('scores_' + key, pd.Series(None, index=df.index, dtype=object)).apply(bounds)
        for pos, label in enumerate(['lower', 'upper']):
            df[f'score_{key}_{label}'] = pd.to_numeric(pd.Series([p[pos] for p in parsed]), errors='coerce')
            df.loc[~df[f'score_{key}_{label}'].between(0, 100), f'score_{key}_{label}'] = float('nan')
    return df

def load_data(path='times_higher_education_rankings.csv'):
    path = Path(path)
    if path.exists():
        return pd.read_csv(path), f'Local file: {path.name}; edition not verified'
    import requests
    from bs4 import BeautifulSoup
    response = requests.get(SOURCE, headers={'User-Agent': 'UniversityScope portfolio research'}, timeout=45)
    response.raise_for_status()
    script = BeautifulSoup(response.text, 'html.parser').find('script', id='__NEXT_DATA__')
    if not script:
        raise RuntimeError('Source layout changed. Upload your previously saved rankings CSV and rerun.')
    payload = json.loads(script.string)
    try:
        records = payload['props']['pageProps']['page']['rankingsTableConfig']['rankingsData']['data']
    except KeyError as error:
        raise RuntimeError('Source data path changed. Upload the original CSV and rerun.') from error
    raw = pd.DataFrame(records)
    raw.to_csv(path, index=False)
    return raw, 'THE latest URL; ranking edition not verified'
