# Constructor University peer benchmark

A complete UniversityScope case study by [Blessing Sekeramavi](https://github.com/BlessingSK1998): turn a ranking snapshot into a reproducible institutional comparison and a concise briefing.

[**Run in Colab**](https://colab.research.google.com/github/BlessingSK1998/UniversityScope/blob/main/reports/constructor-benchmark/Constructor_University_Benchmark.ipynb) · [Notebook](Constructor_University_Benchmark.ipynb) · [Excel workbook](Constructor_University_Benchmark.xlsx) · [Five-slide briefing](Constructor_University_Benchmark_Briefing.pptx)

![Constructor University compared with its selected peer median](comparison.png)

## Question and findings

How does Constructor compare with five ranked German institutions selected by rank-band proximity?

| Component | Constructor | Peer median | Difference (score points) |
| --- | ---: | ---: | ---: |
| Teaching | 39.0 | 34.5 | +4.5 |
| Research | 35.8 | 36.9 | −1.1 |
| Citations | 60.9 | 72.9 | −12.0 |
| Industry income | 84.8 | 76.7 | +8.1 |
| International outlook | 92.6 | 65.4 | +27.2 |

International outlook has the largest positive difference; citations have the largest negative difference. These are component-score points, not percentage-point changes or estimates of causal effects.

## Peer selection

Keep ranked German institutions, exclude Constructor, sort by absolute distance from Constructor's rank-band lower bound (376), break ties alphabetically and take five. Component scores do not determine peer inclusion. Constructor's source rank band is **376–400**.

| Peer | Original rank band | Distance between lower bounds |
| --- | --- | ---: |
| University of Hohenheim | 376–400 | 0 |
| University of Marburg | 376–400 | 0 |
| Justus Liebig University Giessen | 401–450 | 25 |
| Leibniz University Hannover | 351–375 | 25 |
| Saarland University | 401–450 | 25 |

Each median excludes Constructor and uses the five peers. Missing scores remain missing; no zero imputation is used. The analysis retains interval endpoints and compares lower endpoints for ranged scores. All selected component scores in this snapshot have equal lower and upper endpoints.

## Reproduce

1. Open the benchmark notebook in Colab.
2. Supply your `times_higher_education_rankings.csv` when prompted. The original CSV is not committed.
3. Run the four code cells in order. Locally, install `pandas`, `numpy`, `matplotlib` and `ipython`, place the CSV beside the notebook and run it in Jupyter.
4. Inspect the selected peers, score table and charts. The notebook saves two analysis CSVs and a PNG in the working directory.

The prepared Excel workbook has formula-linked medians, gaps, coverage counts and editable charts. The five-slide PowerPoint contains editable charts and a peer table. Rerunning the notebook does not rebuild these Office files automatically.

## Source and limits

Source: [Times Higher Education World University Rankings](https://www.timeshighereducation.com/world-university-rankings/latest/world-ranking). Analyzed source snapshot: 16 October 2026; 3,146 records across 131 location labels. Source SHA256 prefix: `376ff9e47d79`; see the project's [provenance record](../../assets/analysis-summary.json). The ranking edition is unverified because acquisition used a `latest` URL.

This is a country-and-rank comparison. It does not match subject mix, institutional size or mission, explain the causes of score differences, or establish partnership readiness. The saved results are a historical snapshot and can change with a different input. Review publisher reuse terms before acquiring or redistributing data.
