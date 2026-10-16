"""UniversityScope: source loading and conservative numeric parsing."""
from pathlib import Path
import json
import re
import hashlib
from datetime import datetime, timezone
import pandas as pd

SOURCE = 'https://www.timeshighereducation.com/world-university-rankings/latest/world-ranking'

def bounds(value):
    if pd.isna(value):
        return None, None
    text = str(value).strip().lstrip('=').strip()
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
    if raw.empty:
        raise ValueError('The university table is empty. Upload a CSV containing institution records.')
    df = raw.copy().reset_index(drop=True)
    df['name'] = df['name'].fillna('Unnamed institution').astype(str).str.strip()
    df['location'] = df['location'].fillna('Unknown').astype(str).str.strip()
    df['rank_original'] = df['rank'].fillna('Unknown').astype(str)
    pairs = df['rank'].apply(bounds)
    df['rank_lower_bound'] = [p[0] for p in pairs]
    df['rank_upper_bound'] = [p[1] for p in pairs]
    valid_rank = df.rank_lower_bound.ge(1) & df.rank_lower_bound.mod(1).eq(0) & (df.rank_upper_bound.isna() | (df.rank_upper_bound.ge(1) & df.rank_upper_bound.mod(1).eq(0)))
    df.loc[~valid_rank,['rank_lower_bound','rank_upper_bound']] = float('nan')
    disabled = df.get('disabled', pd.Series(False, index=df.index)).astype(str).str.strip().str.lower().isin(['true', '1', '1.0'])
    df['academic_status'] = 'Unknown/unranked'
    df.loc[df['rank_lower_bound'].notna(), 'academic_status'] = 'Ranked'
    df.loc[df['rank_original'].str.contains('reporter', case=False), 'academic_status'] = 'Reporter'
    df.loc[disabled, 'academic_status'] = 'Disabled'
    for key in ['overall', 'teaching', 'research', 'citations', 'industry_income', 'international_outlook']:
        parsed = df.get('scores_' + key, pd.Series(None, index=df.index, dtype=object)).apply(bounds)
        for pos, label in enumerate(['lower', 'upper']):
            df[f'score_{key}_{label}'] = pd.to_numeric(pd.Series([p[pos] for p in parsed]), errors='coerce')
        valid = df[f'score_{key}_lower'].between(0, 100) & df[f'score_{key}_upper'].between(0, 100)
        df.loc[~valid, [f'score_{key}_lower', f'score_{key}_upper']] = float('nan')
        df[f'score_{key}_invalid_flag'] = df.get('scores_' + key, pd.Series(None, index=df.index, dtype=object)).notna() & ~valid
    return df

def load_data(path='times_higher_education_rankings.csv'):
    path = Path(path)
    if path.exists():
        fingerprint = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        return pd.read_csv(path), f'Local snapshot {path.name} · SHA256 {fingerprint} · ranking edition unverified'
    import requests
    from bs4 import BeautifulSoup
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=Retry(total=2, backoff_factor=0.5, status_forcelist=[429,500,502,503,504], allowed_methods=['GET'])))
    try:
        response = session.get(SOURCE, headers={'User-Agent': 'UniversityScope portfolio research'}, timeout=(10,30))
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError('Source is unavailable. Upload times_higher_education_rankings.csv and rerun; your saved snapshot will be used without a network request.') from error
    script = BeautifulSoup(response.text, 'html.parser').find('script', id='__NEXT_DATA__')
    if not script:
        raise RuntimeError('Source layout changed. Upload your previously saved rankings CSV and rerun.')
    payload = json.loads(script.string)
    try:
        records = payload['props']['pageProps']['page']['rankingsTableConfig']['rankingsData']['data']
    except KeyError as error:
        raise RuntimeError('Source data path changed. Upload the original CSV and rerun.') from error
    raw = pd.DataFrame(records)
    if raw.empty or not {'name','rank','location'}.issubset(raw):
        raise RuntimeError('Source returned no valid university table. Upload your saved rankings CSV.')
    raw.to_csv(path, index=False)
    metadata = {'url':SOURCE,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'page_title':BeautifulSoup(response.text,'html.parser').title.get_text() if BeautifulSoup(response.text,'html.parser').title else None,'ranking_edition':None}
    path.with_suffix('.metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    return raw, f"THE latest URL · retrieved {metadata['retrieved_utc']} · ranking edition unverified"
