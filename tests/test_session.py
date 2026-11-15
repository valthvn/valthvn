"""Check real-day semantics, safe motion and the actual README navigation."""
import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import render_session as session

NS = {'s':'http://www.w3.org/2000/svg'}
ASSETS = ['tableau','activity']+[f'cartel-{i:02d}' for i in range(1,len(session.PROJECTS)+1)]


class SessionTests(unittest.TestCase):
    def data(self):
        return json.loads((ROOT/'data/contributions.json').read_text(encoding='utf-8'))

    def test_window_is_365_real_days_ending_at_the_last_observed_date(self):
        days = session.normalize_days(self.data())
        self.assertEqual(len(days),365)
        self.assertEqual((days[-1]['date']-days[0]['date']).days,364)
        broken = self.data()
        broken['days'] = broken['days'][:100]+broken['days'][101:]
        with self.assertRaises(KeyError):
            session.normalize_days(broken)

    def test_each_light_is_a_real_active_day_of_the_last_90(self):
        window = session.normalize_days(self.data())[-90:]
        active = {d['date'].isoformat():d['count'] for d in window if d['count']}
        root = ET.fromstring(session.activity(self.data()))
        lights = {g.get('data-day'):int(g.get('data-count')) for g in root.iter('{http://www.w3.org/2000/svg}g') if g.get('data-day')}
        self.assertEqual(lights,active)
        body = session.activity(self.data())
        self.assertIn(f"{sum(d['count'] for d in window)} in the last 90",body)
        self.assertIn(f"as of {window[-1]['date'].isoformat()}",body)

    def test_no_scripts_external_assets_and_reduced_motion(self):
        for name in ASSETS:
            body = (ROOT/'assets/session'/f'{name}.svg').read_text(encoding='utf-8')
            ET.fromstring(body)
            self.assertIn('prefers-reduced-motion:reduce',body)
            self.assertIn('animation:none',body)
            self.assertNotIn('<script',body)
            self.assertNotIn('<foreignObject',body)
            self.assertNotIn('href=',body)

    def test_all_readme_assets_and_clickable_labels(self):
        body = (ROOT/'README.md').read_text(encoding='utf-8')
        self.assertEqual(body,session.readme())
        paths = re.findall(r'src="\./([^"]+)"',body)
        self.assertEqual(sorted(paths),sorted(f'assets/session/{name}.svg' for name in ASSETS))
        for path in paths:
            self.assertTrue((ROOT/path).is_file(),path)
        self.assertEqual(body.count('<details>'),2)
        for project in session.PROJECTS:
            self.assertIn('href="https://github.com/valthvn/'+project['repo']+'"',body)

    def test_no_stale_assets_and_no_full_canvas_background(self):
        self.assertEqual(sorted(p.stem for p in (ROOT/'assets/session').glob('*.svg')),sorted(ASSETS))
        for name in ASSETS:
            root = ET.fromstring((ROOT/f'assets/session/{name}.svg').read_text(encoding='utf-8'))
            for rect in root.findall('s:rect',NS):
                self.assertFalse(rect.get('x') in (None,'0') and rect.get('y') in (None,'0')
                                 and rect.get('width')==root.get('width') and rect.get('height')==root.get('height'))


if __name__ == '__main__':
    unittest.main()
