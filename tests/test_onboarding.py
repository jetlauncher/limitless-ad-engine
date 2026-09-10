import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import engine
import onboarding
import start
import student


class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.brand = {'name':'ร้านกาแฟตัวอย่าง', 'audience':'คนทำงานที่บ้าน',
                      'offer':'เมล็ดกาแฟคั่วกลาง ถุงละ 250 กรัม', 'pain':'เลือกกาแฟไม่ตรงรสที่ชอบ',
                      'differentiator':'มีรายละเอียดแหล่งปลูก', 'proof':'ยังไม่มีหลักฐานที่ตรวจแล้ว',
                      'cta':'ดูสินค้า', 'destination':'https://example.org/coffee',
                      'tone':'อบอุ่น', 'goal':'สอบถามสินค้า',
                      'context':{'notes':'PRIVATE_ONLY_NOTE_749', 'documents':[{'name':'brief.txt','text':'PRIVATE_DOC_913'}]}}
    def tearDown(self):
        self.tmp.cleanup()
    def test_interview_reprompts_and_preserves_context(self):
        doc = self.root / 'context.txt'
        doc.write_text('ข้อมูล\nสองบรรทัด', encoding='utf-8')
        answers = iter(['', 'ร้านกาแฟ', 'คนทำงาน', 'กาแฟ', 'เลือกรสไม่ถูก', '', '', '',
                        'javascript:bad', 'https://example.org/', '', '', 'บริบทที่มี', str(doc), '',
                        'red', '#123456', 'th', 'TH',
                        'คู่แข่ง A', 'https://example.org/a', 'การเล่าเรื่อง', 'abc', '1234', 'n', '',
                        'แบรนด์ B', '', 'ภาพสินค้า', '', '', 'y'])
        brand, watchlist, color = onboarding.interview(input_fn=lambda _:next(answers), output=lambda _:None)
        self.assertEqual(brand['context']['documents'][0]['text'], 'ข้อมูล\nสองบรรทัด')
        self.assertEqual(color, '#123456')
        self.assertEqual([r['relationship'] for r in watchlist], ['competitor','aspiration'])
        self.assertTrue(all(not r['enabled'] for r in watchlist))
        self.assertEqual(engine.plan(watchlist), [])
    def test_context_rejects_binary_and_oversized(self):
        file = self.root/'brief.pdf'; file.write_bytes(b'PDF')
        with self.assertRaises(ValueError): onboarding.context_file(file)
        file = self.root/'brief.txt'; file.write_bytes(b'a'*100_001)
        with self.assertRaises(ValueError): onboarding.context_file(file)
    def test_real_project_renders_and_keeps_context_private(self):
        out = self.root/'project'
        with patch('urllib.request.urlopen', side_effect=AssertionError('No outbound calls allowed')):
            onboarding.create_project(self.brand, [], '#123456', out)
            student.build_project(out, self.root/'site')
        from PIL import Image
        image = Image.open(out/'assets/my-ad-01.png')
        self.assertEqual(image.size, (1080,1350))
        self.assertEqual(image.getpixel((85,1100)), (18,52,86))
        rows = engine.read(self.root/'site/catalog.json')
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(row['status']=='draft' and not row.get('download') for row in rows))
        text = (self.root/'site/catalog.json').read_text(encoding='utf-8')
        self.assertNotIn('PRIVATE_ONLY', text); self.assertNotIn('PRIVATE_DOC', text)
        self.assertEqual(engine.read(out/'creative-brief.json')['brand']['context'], self.brand['context'])
        self.assertEqual(engine.read(out/'creative-brief.json')['research_status'], 'not_collected')
        packs, _ = student.prepare(out)
        self.assertTrue(engine.validate_pack(packs[0], out/'assets', approved=True))
    def test_existing_project_is_not_overwritten(self):
        out = self.root/'existing'; out.mkdir(); (out/'keep.txt').write_text('keep')
        with self.assertRaises(ValueError): onboarding.create_project(self.brand, [], '#123456', out)
        self.assertEqual((out/'keep.txt').read_text(), 'keep')
    def test_failed_render_does_not_leave_partial_project(self):
        with patch('scripts.render_pack.render', side_effect=ValueError('Bad input')):
            with self.assertRaises(ValueError):
                onboarding.create_project(self.brand, [], '#123456', self.root/'failed')
        self.assertFalse((self.root/'failed').exists())
        self.assertFalse(list(self.root.glob('.intake-*')))
    def test_rerun_reopens_project_without_interview(self):
        project = onboarding.create_project(self.brand, [], '#123456', self.root/'one')
        with patch.object(start, 'ROOT', self.root), patch.object(start, 'STATE', self.root/'.ad-engine/active.json'):
            start.remember(project)
            with patch('onboarding.interview', side_effect=AssertionError('Unexpected interview')):
                self.assertEqual(start.main(['--setup-only']), 0)
            self.assertEqual(start.saved_project(), project.resolve())
    def test_cancel_preserves_current_project(self):
        project = self.root/'old'; project.mkdir(); engine.write(project/'brand.json',self.brand)
        with patch.object(start, 'ROOT', self.root), patch.object(start, 'STATE', self.root/'.ad-engine/active.json'):
            start.remember(project)
            with patch('onboarding.interview', return_value=None):
                self.assertEqual(start.main(['--new','--setup-only']), 0)
            self.assertEqual(start.saved_project(), project.resolve())

if __name__ == '__main__': unittest.main()
