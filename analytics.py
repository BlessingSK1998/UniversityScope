"""Reproducible descriptive analysis; no inferred institutional mission labels."""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

METRICS = ['teaching', 'research', 'citations', 'industry_income', 'international_outlook']
FEATURES = ['score_' + key + '_lower' for key in METRICS]

def cluster_profiles(df):
    complete = df.loc[df.academic_status.eq('Ranked')].dropna(subset=FEATURES).copy()
    empty = pd.DataFrame(columns=['k','silhouette'])
    if len(complete) < 10 or len(complete[FEATURES].drop_duplicates()) < 3:
        return complete, empty, pd.DataFrame(), None
    X = StandardScaler().fit_transform(complete[FEATURES])
    results, models = [], {}
    for k in range(2, min(6,len(complete[FEATURES].drop_duplicates()))):
        model = KMeans(n_clusters=k,n_init=10,random_state=42).fit(X)
        if len(set(model.labels_)) < 2:
            continue
        score = silhouette_score(X, model.labels_, sample_size=min(2000,len(X)),random_state=42)
        results.append({'k': k,'silhouette':float(score)})
        models[k] = model
    if not results:
        return complete, empty, pd.DataFrame(), None
    scores = pd.DataFrame(results).sort_values('silhouette',ascending=False).reset_index(drop=True)
    best = int(scores.iloc[0]['k'])
    labels = models[best].labels_
    # Sort labels by centroid teaching score so charts stay interpretable across runs.
    order = np.argsort(models[best].cluster_centers_[:,0])
    relabel = {int(old):int(new) for new,old in enumerate(order)}
    complete['cluster'] = [relabel[int(label)] for label in labels]
    profiles = complete.groupby('cluster')[FEATURES].mean()
    return complete, scores, profiles, best

def quality_report(raw, df):
    return {'records':len(df),'locations':int(df.location.nunique()),'statuses':{str(k):int(v) for k,v in df.academic_status.value_counts().items()},'duplicate_name_location_rows':int(df.duplicated(['name','location'],keep=False).sum()),'unparsed_rank_rows':int((df.academic_status.eq('Unknown/unranked')).sum()),'open_ended_rank_rows':int((df.rank_lower_bound.notna() & df.rank_upper_bound.isna()).sum()),'missing_scores':{key:int(df['score_'+key+'_lower'].isna().sum()) for key in ['overall']+METRICS},'invalid_score_fields':{key:int(df['score_'+key+'_invalid_flag'].sum()) for key in ['overall']+METRICS}}
