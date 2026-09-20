import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_job as jobs
import subtitles as subs
import batch_plan
import media_audit
import media_ops
import manifest

CFG = {'kind':'image','model':'test-provider/fake-model','params':{'prompt':'Offline fixture; never submitted'}}

class JobTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name)
        self.config=self.root/'config.json';self.config.write_text(json.dumps(CFG))
        self.run=self.root/'run';jobs.prepare(self.config,self.run)
    def tearDown(self):self.t.cleanup()
    def test_prepare_plan_matches(self):self.assertEqual(jobs.read_plan(self.run)['config'],CFG)
    def test_prepare_refuses_existing(self):
        with self.assertRaises(FileExistsError):jobs.prepare(self.config,self.run)
    def test_approval_required_before_marker(self):
        with patch.object(jobs,'invoke') as fn:
            with self.assertRaises(ValueError):jobs.submit(self.run,'fake',False)
            fn.assert_not_called();self.assertFalse((self.run/'attempt.json').exists())
    def test_submit_retains_id_even_nonzero(self):
        with patch.object(jobs,'invoke',return_value=(9,'{"id":"p1","status":"processing"}','warning')):
            r=jobs.submit(self.run,'fake',True)
        self.assertEqual(r['prediction_id'],'p1');self.assertEqual(r['state'],'pending');self.assertEqual(r['cli_exit_code'],9)
    def test_duplicate_never_invokes_again(self):
        with patch.object(jobs,'invoke',return_value=(0,'{"id":"p1","status":"starting"}','')) as fn:
            jobs.submit(self.run,'fake',True)
            with self.assertRaises(FileExistsError):jobs.submit(self.run,'fake',True)
            self.assertEqual(fn.call_count,1)
    def test_timeout_is_unknown_and_marker_survives(self):
        with patch.object(jobs,'invoke',return_value=(None,'','local timeout')):
            r=jobs.submit(self.run,'fake',True)
        self.assertEqual(r['state'],'unknown');self.assertTrue((self.run/'attempt.json').exists())
    def test_malformed_receipt_unknown(self):
        with patch.object(jobs,'invoke',return_value=(0,'<html>error</html>','')):
            self.assertEqual(jobs.submit(self.run,'fake',True)['state'],'unknown')
    def test_conflicting_ids_unknown(self):
        with patch.object(jobs,'invoke',return_value=(0,'{"id":"a","prediction_id":"b"}','')):
            self.assertIsNone(jobs.submit(self.run,'fake',True)['prediction_id'])
    def test_observe_failed_despite_exit_zero(self):
        jobs.save(self.run/'submission-state.json',{'prediction_id':'p1'})
        with patch.object(jobs,'invoke',return_value=(0,'{"prediction_id":"p1","status":"failed"}','')):
            self.assertEqual(jobs.observe(self.run,'fake',False,30)['state'],'remote_failed')
    def test_observe_wrong_id_unknown(self):
        jobs.save(self.run/'submission-state.json',{'prediction_id':'p1'})
        with patch.object(jobs,'invoke',return_value=(0,'{"prediction_id":"p2","status":"completed"}','')):
            self.assertEqual(jobs.observe(self.run,'fake',False,30)['state'],'unknown')
    def test_observe_needs_reliable_id(self):
        jobs.save(self.run/'submission-state.json',{'prediction_id':None})
        with patch.object(jobs,'invoke') as fn:
            with self.assertRaises(ValueError):jobs.observe(self.run,'fake',False,30)
            fn.assert_not_called()
    def test_params_tamper_blocked(self):
        jobs.save(self.run/'params.json',{'prompt':'changed'})
        with self.assertRaises(ValueError):jobs.read_plan(self.run)
    def test_plan_tamper_blocked(self):
        p=jobs.load_json(self.run/'plan.json');p['config']['model']='other/model';jobs.save(self.run/'plan.json',p)
        with self.assertRaises(ValueError):jobs.read_plan(self.run)
    def test_args_are_a_list_with_absolute_config(self):
        a=jobs.generation_args(CFG,self.run)
        self.assertEqual(a[:3],['generate','image','test-provider/fake-model'])
        self.assertEqual(a[-1],'@'+str((self.run/'params.json').resolve()))

class ConfigTests(unittest.TestCase):
    def test_reserved(self):
        for key in ['model','Authorization','api_key','token','access_token']:
            with self.subTest(key=key),self.assertRaises(ValueError):jobs.validate_config({**CFG,'params':{key:'x'}})
    def test_placeholder(self):
        for model in ['REPLACE_WITH_MODEL','填入模型','-bad','bad model',' foo/bar']:
            with self.subTest(model=model),self.assertRaises(ValueError):jobs.validate_config({**CFG,'model':model})
    def test_atfile(self):
        with self.assertRaises(ValueError):jobs.validate_config({**CFG,'params':{'images':['@private.png']}})
    def test_nan(self):
        with self.assertRaises(ValueError):jobs.validate_config({**CFG,'params':{'x':float('nan')}})
    def test_duplicate_keys(self):
        with self.assertRaises(ValueError):jobs.reject_duplicates([('a',1),('a',2)])
    def test_unknown_status(self):self.assertEqual(jobs.classify({'status':'brand-new-status'}),'unknown')
    def test_rest_not_cli(self):self.assertEqual(jobs.classify({'data':{'status':'completed'}}),'unknown')

class SubtitleTests(unittest.TestCase):
    def test_roundtrip(self):
        x=[{'start':.25,'end':1.75,'text':'字幕测试'}]
        self.assertEqual(subs.validate(subs.parse_srt(subs.as_srt(x))),x)
    def test_negative_time(self):
        with self.assertRaises(ValueError):subs.validate([{'start':-1,'end':2,'text':'x'}])
    def test_boolean_time(self):
        with self.assertRaises(ValueError):subs.validate([{'start':False,'end':2,'text':'x'}])
    def test_overlap_requires_review(self):
        s=[{'start':0,'end':2,'text':'x'},{'start':1,'end':3,'text':'y'}]
        with self.assertRaises(ValueError):subs.validate(s)
        self.assertEqual(len(subs.validate(s,allow_overlap=True)),2)
    def test_duration_overrun(self):
        with self.assertRaises(ValueError):subs.validate([{'start':1,'end':4,'text':'x'}],duration=3)
    def test_blank_cue(self):
        with self.assertRaises(ValueError):subs.validate([{'start':0,'end':1,'text':' '}])
    def test_bad_stamp(self):
        with self.assertRaises(ValueError):subs.parse_stamp('00:70:00,000')
    def test_millisecond_rounding_zero(self):
        with self.assertRaises(ValueError):subs.validate([{'start':.00001,'end':.00002,'text':'x'}])
    def test_offset_merge(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td);(r/'a.json').write_text(json.dumps([{'start':.2,'end':1,'text':'x'}]))
            x=subs.merge_chunks([{'offset_seconds':10,'segments_file':'a.json'}],r)
            self.assertAlmostEqual(x[0]['start'],10.2);self.assertEqual(x[0]['end'],11)
    def test_path_escape(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):subs.merge_chunks([{'offset_seconds':0,'segments_file':'../a.json'}],Path(td))

class BatchAndMediaTests(unittest.TestCase):
    def rows(self,text,maximum=3,field=None):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'table.csv';p.write_text(text)
            return batch_plan.build_rows(p,'test/model',field,maximum)
    def test_batch_no_submit(self):
        with patch.object(jobs,'invoke') as fn:
            self.assertEqual(len(self.rows('sku,prompt\none,test\ntwo,test\n')),2);fn.assert_not_called()
    def test_case_insensitive_duplicate(self):
        with self.assertRaises(ValueError):self.rows('sku,prompt\nABC,x\nabc,y\n')
    def test_path_sku(self):
        with self.assertRaises(ValueError):self.rows('sku,prompt\n../bad,x\n')
    def test_limit(self):
        with self.assertRaises(ValueError):self.rows('sku,prompt\na,x\nb,y\n',maximum=1)
    def test_reference_requires_field(self):
        with self.assertRaises(ValueError):self.rows('sku,prompt,reference_url\na,x,https://example.com/a.png\n')
    def test_fps(self):self.assertAlmostEqual(media_audit.rate('30000/1001'),29.97002997)
    def test_unknown_fps(self):
        for x in ['0/0','N/A',None,'inf']:self.assertIsNone(media_audit.rate(x))
    def test_summary_retains_rotation_and_sar(self):
        x=media_audit.summarize({'streams':[{'codec_type':'video','width':180,'height':320,'sample_aspect_ratio':'1:1','side_data_list':[{'rotation':90}]}]})
        self.assertEqual(x['video'][0]['rotation'],[90]);self.assertEqual(x['video'][0]['sample_aspect_ratio'],'1:1')
    def test_bad_image_dimensions(self):
        with self.assertRaises(ValueError):media_ops.fit_filter(0,100,'contain')
    def test_hash_file(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'file';p.write_bytes(b'abc');self.assertEqual(manifest.sha256(p),hashlib.sha256(b'abc').hexdigest())

if __name__=='__main__':unittest.main()
