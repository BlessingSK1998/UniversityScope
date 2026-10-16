import tempfile
import unittest
from pathlib import Path
import pandas as pd
from pipeline import clean, bounds, load_data
from analytics import cluster_profiles
from dashboard import build_dashboard
from geography import country_codes
from visuals import split_dateline

class DataTests(unittest.TestCase):
    def test_country_aliases_and_unresolved_territories(self):
        codes=country_codes(['Turkey','Türkiye','Palestine','Northern Cyprus','Kosovo'])
        self.assertEqual(codes['Turkey']['iso'],'TUR')
        self.assertEqual(codes['Türkiye']['iso'],'TUR')
        self.assertEqual(codes['Palestine']['iso'],'PSE')
        self.assertIsNone(codes['Northern Cyprus']);self.assertIsNone(codes['Kosovo'])

    def test_dateline_geometry_is_split(self):
        parts=split_dateline([(170,10),(-170,10),(-170,20),(170,20),(170,10)])
        self.assertEqual(len(parts),2)
        for part in parts:
            self.assertTrue(all(-180<=x<=180 for x,y in part))
            self.assertTrue(all(abs(a[0]-b[0])<=20 for a,b in zip(part,part[1:])))
    def test_rank_bands_and_statuses_preserve_uncertainty(self):
        raw=pd.DataFrame({'name':['A','B','C','D','E'],'location':['Germany']*5,'rank':['= 3','301–325','2001+','Reporter',None],'disabled':['False','false','false','true','false']})
        out=clean(raw)
        self.assertEqual(out.academic_status.tolist(),['Ranked','Ranked','Ranked','Disabled','Unknown/unranked'])
        self.assertEqual(out.rank_lower_bound.iloc[:3].tolist(),[3,301,2001])
        self.assertTrue(pd.isna(out.rank_upper_bound.iloc[2]))
        self.assertEqual(out.name.tolist(),raw.name.tolist())

    def test_score_zero_missing_and_invalid_ranges(self):
        raw=pd.DataFrame({'name':['A','B','C','D','E'],'location':['Germany']*5,'rank':['1']*5,'scores_teaching':['0',None,'90–95','80–120','60–40']})
        out=clean(raw)
        self.assertEqual(out.score_teaching_lower.iloc[0],0)
        self.assertTrue(out.score_teaching_lower.iloc[[1,3,4]].isna().all())
        self.assertTrue(out.score_teaching_upper.iloc[[1,3,4]].isna().all())
        self.assertEqual(out.score_teaching_upper.iloc[2],95)
        self.assertEqual(out.score_teaching_invalid_flag.tolist(),[False,False,False,True,True])

    def test_bad_schema_empty_and_fractional_rank(self):
        with self.assertRaisesRegex(ValueError,'Missing columns'):clean(pd.DataFrame({'name':['A']}))
        with self.assertRaisesRegex(ValueError,'empty'):clean(pd.DataFrame(columns=['name','location','rank']))
        out=clean(pd.DataFrame({'name':['A'],'location':['Germany'],'rank':['1.5']}))
        self.assertEqual(out.academic_status.iloc[0],'Unknown/unranked')

    def test_local_input_never_needs_network(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'rankings.csv';path.write_text('name,location,rank\nA,Germany,1\n')
            raw,description=load_data(path)
            self.assertEqual(len(raw),1);self.assertIn('SHA256',description)

    def test_small_cohort_does_not_invent_clusters(self):
        df=clean(pd.DataFrame({'name':['A'],'location':['Germany'],'rank':['Reporter']}))
        _,scores,profiles,best=cluster_profiles(df)
        self.assertIsNone(best);self.assertTrue(scores.empty);self.assertTrue(profiles.empty)

    def test_html_safely_embeds_names_and_boundaries(self):
        df=clean(pd.DataFrame({'name':['</script><script>alert(1)</script>'],'location':['Germany'],'rank':['1']}))
        with tempfile.TemporaryDirectory() as folder:
            document=build_dashboard(df,'test',output=Path(folder)/'dashboard.html')
            self.assertNotIn('</script><script>alert',document)
            self.assertNotIn('__PAYLOAD__',document)
            self.assertIn('"world":',document)

if __name__=='__main__':unittest.main()
