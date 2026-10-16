# Methods and data

## Snapshot and scope

The saved input has 3,146 institution records across 131 location labels. The source is the Times Higher Education latest world-ranking page. The edition was not verified; the file hash in `assets/analysis-summary.json` identifies the analyzed snapshot. A local input is reused without making a network request. New successful retrievals write a timestamp, URL, page title and SHA256 sidecar locally.

The source can change its embedded JSON structure or deny requests. In that case, upload the saved CSV and rerun. Do not substitute invented data.

## Parsing and record classification

The pipeline preserves every row and its original source fields. Numeric and tied ranks have equal bounds. Finite rank bands retain lower and upper endpoints; an open rank such as `2001+` retains only the lower bound. Invalid and fractional rank strings are left unknown.

A disabled flag takes precedence over rank status. Explicit reporter labels become Reporter. Otherwise a valid parsed rank becomes Ranked; missing or unknown rank text remains Unknown/unranked. These are source-record classifications, not independent judgments about accreditation.

Score intervals must have ordered bounds within 0–100. An invalid interval makes both parsed endpoints missing and sets a field-level invalid flag. Missing input remains missing. No zero imputation is used. Charts compare lower score bounds, which are conservative endpoints rather than exact values for ranged scores.

## Geography

Country aliases are resolved explicitly in `geography.py` and shared by both visualization paths. Turkey and Türkiye resolve to TUR, and Palestine resolves to PSE. Northern Cyprus and Kosovo are retained as source location labels without inventing ISO matches. This resolution is a technical join for geometry, not a position on territorial status.

The embedded world geometry comes from `world-atlas@2.0.2/countries-110m.json`, based on Natural Earth. Source: https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json. Repository: https://github.com/topojson/world-atlas. Natural Earth data is public domain; world-atlas code is ISC licensed. Administrative boundaries are a cartographic dataset, not a claim of territorial authority.

The static world map decodes the source TopoJSON arcs and clips polygons at the international date line, using an equirectangular view. It shows ranked institutions and uses a logarithmic count colour scale. The interactive world views use country counts for the current selection, with square-root colour/height scaling. Their colours are therefore not numerically interchangeable with the static map. The interactive flat view uses the D3 Natural Earth projection.

Country-code matching and boundary coverage are different counts. Of 2,224 ranked records, 2,200 appear in the low-resolution geometry. Small territories may be absent. No country aggregate is presented as a university campus coordinate.

## Analysis

Descriptive charts use the ranked cohort unless otherwise labeled. Missingness compares all source statuses. Pearson correlations use pairwise complete observations and are associations, not causal estimates.

K-Means uses teaching, research, citations, industry income and international outlook lower scores. It excludes name, geography, overall score and rank. Complete cases are standardized with StandardScaler. Candidate K values 2–5 are evaluated using silhouette score, with a reproducible sample of at most 2,000 rows. K-Means uses random_state=42 and n_init=10. The best tested K is selected; stability under other features, scales and samples is not established. Neutral labels are ordered by centroid teaching score, and the dashboard uses those fitted labels without heuristic replacements. Filtering changes the shown members without refitting the model.

## Reproduction and display

`python visuals.py` generates SVG/PNG charts, a JSON summary and the dashboard from one cleaned snapshot. `build_notebook.py --with-results` embeds the canonical source files and the calculated PNG results into a portable notebook. `--check` detects notebook source drift. Large image diffs can be collapsed by GitHub; the README provides individual SVG previews.

The dashboard embeds the data and country boundaries, but loads Plotly.js, D3, Globe.gl and topojson-client from pinned jsDelivr URLs. WebGL availability affects the 3D globe. GitHub notebook previews cannot execute JavaScript; use Colab or the generated standalone HTML. There is no automatic public hosting configuration.

## Limits

The snapshot is not a census of universities. Rankings, source classifications and clustering cannot establish institutional mission, research complementarity, willingness to collaborate or funding eligibility. Raw input files and generated institution-level HTML are excluded from version control. Check publisher reuse terms before redistribution.
