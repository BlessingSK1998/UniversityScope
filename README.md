# UniversityScope
### Global university intelligence · interactive notebook dashboard

Explore 3,146 institution records through an embedded dashboard with a **3D globe, 2D world map, filters, score comparisons and downloadable shortlists**.

**[Open in Google Colab](https://colab.research.google.com/github/BlessingSK1998/UniversityScope/blob/main/UniversityScope.ipynb)** · [View notebook](UniversityScope.ipynb)

Built by [Blessing Sekeramavi](https://github.com/BlessingSK1998), combining data science with international university outreach.

## See the dashboard
1. Open the Colab link above.
2. Select **Runtime → Run all**.
3. Scroll to **Launch the interactive dashboard**. The dashboard displays inside the notebook; scroll within its frame for comparisons and the explorer.

The notebook is self-contained. Upload your existing `times_higher_education_rankings.csv` through Colab's Files sidebar to reuse it; otherwise it attempts source retrieval. Internet access is required for dependencies, map boundaries and visualization libraries.

**GitHub disables JavaScript in notebook previews. Use Colab to interact with the dashboard.** You can also download the generated `universityscope_dashboard.html` from Colab and open it in a browser with internet access. There is no hosted public dashboard deployment yet.

## What's inside
| Feature | Behaviour |
| --- | --- |
| 3D globe | Real country boundary polygons, heights and colours representing institution counts |
| 2D world map | Country choropleth with counts and click-to-filter interaction |
| Search and filters | Institution name, country/territory, ranking status and score dimension |
| Performance analysis | Country coverage and teaching versus research scatterplot |
| Compare | Up to four institutions with aligned component-score bars |
| Explorer | Original ranks/bands, status and score intervals; all matches exported to CSV |
| Clustering | Complete-case component scores; K=2–5 evaluated by silhouette, fitted labels exported |

The maps aggregate institutions **by country**. They do not imply verified campus coordinates. Unresolved country codes are counted visibly. The 3D map depends on WebGL; if its libraries fail to load, the dashboard switches to the 2D view and shows an error.

## Local use
```bash
git clone https://github.com/BlessingSK1998/UniversityScope.git
cd UniversityScope
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab UniversityScope.ipynb
```

The notebook embeds the Python helpers and HTML template for portability. The matching `pipeline.py`, `dashboard.py` and `dashboard.html` are included for inspection and reuse. If you edit these files, update the corresponding notebook cells as well.

## Data and methodology
Source: [Times Higher Education World University Rankings](https://www.timeshighereducation.com/world-university-rankings/latest/world-ranking). Validation retrieval on 16 October 2026 returned **3,146 records across 131 locations**. Current classification: **2,224 ranked, 821 reporter and 101 disabled**. The source URL uses `latest`; ranking edition is not independently verified, and future counts may change.

- Rank and score intervals retain separate lower and upper bounds. Open-ended ranks retain an unknown upper bound.
- Missing values remain missing. Valid zeros are retained.
- Charts use lower score bounds, which are not exact scores when a range is reported.
- Status classification uses source rank text/numeric bounds and the disabled flag; missing ranks remain unknown rather than automatically becoming reporters.
- Country matching uses ISO country codes through pycountry; world geometry comes from Natural Earth via world-atlas. Small territories may be absent from the low-resolution boundary dataset.
- Clustering excludes overall score, rank and location. It uses standardized complete component-score records and selects K by silhouette. There are no heuristic labels pretending to be fitted clusters. Stability and external validity remain untested.
- Rankings support preliminary screening; they do not establish institutional mission, collaboration readiness or funding eligibility.

No raw CSV dataset is committed. Review source access and reuse terms before acquisition or redistribution. This project is not affiliated with the publisher. External chart/map scripts and boundary downloads require network access.

## Validation
Parser edge cases, record preservation, boolean status handling and zero-versus-missing checks passed. Python notebook code and dashboard JavaScript syntax were checked. Live source loading and HTML generation were verified. See the notebook's executed outputs for analysis results; browser rendering remains dependent on Colab, CDN access and WebGL support.
