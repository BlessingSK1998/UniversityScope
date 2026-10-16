# UniversityScope
**University performance analytics and geographic exploration**  
A portfolio project by [Blessing Sekeramavi](https://github.com/BlessingSK1998), connecting data science with international university outreach.

## What this project does
Explores Times Higher Education university ranking data through data-quality auditing, score comparisons, exploratory K-Means clustering and a limited geographic map prototype.

[View the notebook](UniversityScope.ipynb) · [Original Colab notebook](https://colab.research.google.com/drive/1en2zzNR6pxOZt08kDTSGNEFFqh3VbCRG)

## Current status
**Exploratory prototype — not deployed or independently validated.** Saved notebook outputs were inspected for this publication; code was not rerun end-to-end.

| Component | Evidence in the saved notebook |
| --- | --- |
| Acquisition | 3,146 records and 33 source columns |
| Cleaning | Rank/score bounds, missing-value flags and status classification |
| Visual analysis | Geographic distribution, score relationships, performance tiers and missingness |
| Clustering | Standardized component scores; K=2–5 compared using silhouette scores |
| Geographic prototype | 45 institutions attempted; 7 mapped using seeded fallback coordinates |
| Dashboard | Streamlit source written by a notebook cell; launch not verified |

The 3,146 records are not all individually ranked universities. The prototype's cleaning logic reports 2,224 ranked, 821 reporter and 101 disabled records; this classification needs source validation.

## Run
Python 3.10+ is recommended.

```bash
git clone https://github.com/BlessingSK1998/UniversityScope.git
cd UniversityScope
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab UniversityScope.ipynb
```

Run notebook cells in order from this directory. Network access is required to retrieve source data. The page structure may change, and acquisition may fail if the publisher changes its embedded payload.

The notebook creates raw and cleaned CSVs, charts, a map HTML file and `app.py` locally. After generating the cleaned CSV and latest app source:

```bash
streamlit run app.py
```

Colab may already provide most dependencies. Install missing packages with `%pip install -r requirements.txt` after uploading the requirements file. Do not run deployment commands containing credentials in notebook cells.

## Data provenance
Source: [Times Higher Education World University Rankings](https://www.timeshighereducation.com/world-university-rankings/latest/world-ranking). Original notebook saved on 16 October 2026. The acquisition URL uses `latest`; the ranking edition was not verified and reruns may retrieve different records. This project is not affiliated with the publisher.

Raw/cleaned datasets are not redistributed here. Review the source's current access and reuse terms before acquisition or redistribution. Generated interactive HTML may embed source records.

## Important interpretation limits
- Original narrative sample sizes are sometimes inconsistent with saved outputs. Recalculate counts and findings before using them in an interview or report.
- Rank bands are not exact ranks. An early exploratory cell computes midpoints; the later cleaning pipeline retains bounds, but does not yet parse open-ended ranks such as `1501+`.
- Missing demographic fields limit international-student comparisons. Missing values must not be interpreted as zero.
- K=2 achieved silhouette 0.4346; K=3 achieved 0.3461. K=3 is a subjective interpretability choice, not the best silhouette result. Sensitivity claims have not been independently tested.
- Cluster names are inferred from mean ranks rather than established institutional missions. The dashboard's fallback score rules are not actual fitted cluster assignments.
- The app uses zero-filling in some comparisons and shortlist scores, and warns rather than stops when weights do not sum to 100%. These require correction before decision use.
- The current map is **2D Leaflet**, not a 3D globe or an all-university map. Coordinates need verification; geocoder importance is not match confidence. Replace the placeholder contact and review provider policies before geocoding.
- Rankings can support initial screening; they do not establish partnership readiness, funding eligibility or research fit.

## Next improvements
1. Validate ranking edition, classification and open-ended rank parsing.
2. Recalculate all findings directly from the cleaned snapshot.
3. Persist fitted cluster assignments and remove heuristic fallback labels.
4. Preserve missing values and validate shortlist weights.
5. Verify coordinates, report coverage and extend map coverage.
6. Implement a true 3D view and verify a deployed dashboard.

## Skills demonstrated
Python · pandas · data-quality auditing · exploratory analysis · visualization · scikit-learn · geocoding prototyping · Streamlit prototyping
