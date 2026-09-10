"""Record a human's completed review into a NEW pack file. This never launches ads."""
import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import read,write,validate_pack,approval_hash,now
p=argparse.ArgumentParser();p.add_argument('--pack',required=True);p.add_argument('--root',required=True);p.add_argument('--out',required=True);p.add_argument('--reviewer',required=True)
p.add_argument('--confirm-reviewed',action='store_true',help='Confirm you checked visual, offer, claims, rights, and destination')
a=p.parse_args();pack=read(a.pack);errors=validate_pack(pack,a.root)
if errors:raise SystemExit('; '.join(errors))
if pack.get('demo'):raise SystemExit('Demo packs cannot be approved for launch')
if not a.confirm_reviewed:raise SystemExit('Complete the human review first, then pass --confirm-reviewed')
pack['approval']={'reviewer':a.reviewer,'reviewed_at':now(),'offer_checked':True,'claims_checked':True,'visual_checked':True,'destination_checked':True,'content_sha256':approval_hash(pack)}
pack['status']='approved';write(a.out,pack);print('Approved copy saved. Ads have NOT been launched.')
