import copy,json,struct,tempfile,unittest,zipfile,zlib
from pathlib import Path
from unittest.mock import patch
import engine

def png():
    def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1080,1350,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'\0'*3240)*1350))+chunk(b'IEND',b'')

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);data=png();(self.root/'ad.png').write_bytes(data)
        self.pack={'id':'test-ad','title':'Test','brand':'Test','angle':'Pain','caption':'บรรทัด 1\n\nบรรทัด 2','headline':'เริ่มได้','cta':'ดูรายละเอียด','destination':'https://example.com/','proof':'Synthetic test','kind':'original','rights':'owned','rights_evidence':'Original fixture','status':'approved','assets':[{'path':'ad.png','order':1,'width':1080,'height':1350,'sha256':engine.digest(data)}]}
        self.pack['approval']={'reviewer':'Test reviewer','reviewed_at':engine.now(),'offer_checked':True,'claims_checked':True,'visual_checked':True,'destination_checked':True,'content_sha256':engine.approval_hash(self.pack)}
    def tearDown(self):self.tmp.cleanup()
    def test_caption_and_asset_export(self):
        p=self.root/'pack.zip';engine.export_pack(self.pack,self.root,p)
        with zipfile.ZipFile(p) as z:
            self.assertEqual(z.read('caption.txt').decode(),self.pack['caption']);self.assertIsNone(z.testzip());self.assertIn('01-ad.png',z.namelist())
    def test_mutation_invalidates_approval(self):
        self.pack['caption']='changed';self.assertIn('Approval does not match current pack content',engine.validate_pack(self.pack,self.root,True))
    def test_reference_and_demo_cannot_export(self):
        for k,v in [('kind','reference'),('demo',True),('status','draft')]:
            p=copy.deepcopy(self.pack);p[k]=v
            with self.assertRaises(ValueError):engine.export_pack(p,self.root,self.root/(k+'.zip'))
    def test_path_escape(self):
        self.pack['assets'][0]['path']='../private.png';self.assertTrue(engine.validate_pack(self.pack,self.root))
    def test_broken_png(self):
        (self.root/'ad.png').write_bytes(b'\x89PNG\r\n\x1a\n');self.assertTrue(engine.validate_pack(self.pack,self.root))
    def test_wrong_dimensions_and_hash(self):
        self.pack['assets'][0]['width']=999;self.pack['assets'][0]['sha256']='bad';self.assertEqual(len(engine.validate_pack(self.pack,self.root)),2)
    def test_normalize_dedupe_and_identity(self):
        rows=engine.read(engine.ROOT/'examples/raw-ads.json');b=engine.read(engine.ROOT/'examples/reference-brand.json');ads,rejected=engine.normalize(rows,b,engine.now());self.assertEqual(len(ads),1);self.assertEqual(len(rejected),1);self.assertIn('\n',ads[0]['caption']);self.assertEqual(ads[0]['performance'],'unknown')
    def test_live_plan_is_bounded_and_dry(self):
        b={'id':'x','name':'x','relationship':'aspiration','page_id':'123','identity_verified':True,'enabled':True,'limit':50,'country':'TH'}
        with patch('engine.request') as req:
            result=engine.start_scrape([b],self.root/'run',None);req.assert_not_called();self.assertEqual(result['max_ads'],50);self.assertEqual(result['jobs'][0]['input']['resultsLimit'],50)
        b['limit']=51
        with self.assertRaises(ValueError):engine.plan([b])
    def test_unverified_brand_blocked(self):
        b=engine.read(engine.ROOT/'examples/reference-brand.json');b['enabled']=True
        with self.assertRaises(ValueError):engine.plan([b])
    def test_legacy_preserves_caption(self):
        a=engine.migrate([{'slug':'a','title':'A','file':'assets/a.png','caption':'หนึ่ง\nสอง'}],'https://example.com/')
        self.assertEqual(a[0]['caption'],'หนึ่ง\nสอง');self.assertEqual(a[0]['status'],'needs_review')
    def test_safe_build_and_download(self):
        self.pack['secret_marker']='PRIVATE';self.pack['approval']['content_sha256']=engine.approval_hash(self.pack)
        out=self.root/'site';engine.build([self.pack],out,self.root);data=engine.read(out/'catalog.json');self.assertNotIn('secret_marker',data[0]);self.assertTrue((out/data[0]['download']).exists());self.assertFalse((out/'raw.json').exists())
        with zipfile.ZipFile(out/data[0]['download']) as z:self.assertNotIn('secret_marker',z.read('manifest.json').decode())
    def test_existing_output_is_never_overwritten(self):
        p=self.root/'keep.json';engine.write(p,{'a':1})
        with self.assertRaises(FileExistsError):engine.write(p,{'a':2})
        self.assertEqual(engine.read(p),{'a':1})

if __name__=='__main__':unittest.main()
