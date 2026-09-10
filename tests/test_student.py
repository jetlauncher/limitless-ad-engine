import json,shutil,tempfile,unittest
from pathlib import Path
import engine,student

class StudentTemplateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.project=self.root/'student'
        shutil.copytree(student.ROOT/'student',self.project)
    def tearDown(self):self.tmp.cleanup()
    def edit(self,file,fn):
        p=self.project/file;data=engine.read(p);fn(data);p.write_text(json.dumps(data,ensure_ascii=False))
    def test_personalized_build_excludes_legacy(self):
        self.edit('brand.json',lambda d:d.update(name='ร้านของฉัน',cta='ดูสินค้า'))
        self.edit('site.json',lambda d:d.update(name='My Shop',headline='My ad library'))
        out=self.root/'site';student.build_project(self.project,out)
        rows=engine.read(out/'catalog.json')
        self.assertEqual(len(rows),3);self.assertTrue(all(r['brand']=='ร้านของฉัน' for r in rows))
        self.assertEqual(engine.read(out/'site.json')['name'],'My Shop')
        self.assertNotIn('limitless-ad-gallery-deploy',(out/'catalog.json').read_text())
    def test_student_does_not_need_asset_hashes(self):
        self.edit('ads.json',lambda d:d[0].update(caption='ข้อความของฉัน\nสองบรรทัด',status='approved',approval={'reviewer':'fake'}))
        packs,_=student.prepare(self.project)
        self.assertEqual(packs[0]['caption'],'ข้อความของฉัน\nสองบรรทัด');self.assertEqual(packs[0]['status'],'draft');self.assertNotIn('approval',packs[0])
        self.assertEqual(len(packs[0]['assets'][0]['sha256']),64)
    def test_bad_color_fails_before_build(self):
        self.edit('site.json',lambda d:d['colors'].update(bg='url(https://example.com/)'))
        with self.assertRaises(ValueError):student.build_project(self.project,self.root/'bad')
        self.assertFalse((self.root/'bad').exists())
    def test_missing_or_escaped_image_rejected(self):
        self.edit('ads.json',lambda d:d[0].update(images=['../../private.png']))
        with self.assertRaises(ValueError):student.prepare(self.project)
    def test_reference_cannot_be_upgraded_in_student_data(self):
        (self.project/'references.json').write_text('[{"kind":"original","status":"approved"}]')
        with self.assertRaises(ValueError):student.prepare(self.project)
