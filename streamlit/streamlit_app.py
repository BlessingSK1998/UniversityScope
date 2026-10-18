"""UniversityScope: published report and interactive CSV explorer."""
from pathlib import Path
import sys
import json
import streamlit as st
import streamlit.components.v1 as components
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline import clean
from dashboard import build_dashboard
import pandas as pd

st.set_page_config(page_title="UniversityScope", layout="wide")
st.title("UniversityScope")
st.caption("Global university performance · Blessing Sekeramavi")
st.write("Explore the published analysis below, or upload the original THE rankings CSV to use the interactive globe, map and institution filters.")
upload = st.file_uploader("THE rankings snapshot", type=["csv"])
if upload is not None:
    try:
        df = clean(pd.read_csv(upload))
        components.html(build_dashboard(df, "User-uploaded snapshot · ranking edition unverified", output=str(Path("/tmp") / "universityscope_dashboard.html")), height=1200, scrolling=True)
    except (ValueError, KeyError, pd.errors.ParserError) as error:
        st.error(str(error))
else:
    st.info("The original rankings CSV is not included in this repository. Upload it above to explore individual institutions.")
    for name, title in [
        ("world-coverage.svg", "Geographic coverage"),
        ("country-coverage.svg", "Countries represented"),
        ("teaching-research.svg", "Teaching and research"),
        ("score-correlations.svg", "Score relationships"),
        ("cluster-profiles.svg", "Cluster profiles"),
        ("data-quality.svg", "Data quality"),
    ]:
        path = ROOT / "assets" / name
        if path.exists():
            st.subheader(title)
            st.image(str(path), use_container_width=True)
with st.expander("Methodology"):
    st.markdown((ROOT / "docs" / "methodology.md").read_text())
