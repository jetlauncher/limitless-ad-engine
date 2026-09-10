"""Student entry point: edit student/ files, then preview or build your own gallery."""
from __future__ import annotations
import argparse
import functools
import http.server
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
import engine

ROOT = Path(__file__).resolve().parent

def load_site(project):
    site=engine.read(Path(project)/'site.json')
    for key in ('name','subtitle','eyebrow','headline','description','footer'):
        if not isinstance(site.get(key),str) or not site[key].strip():
            raise ValueError('site.json: fill in '+key)
    allowed=('bg','surface','gold','ink','muted','line')
    if not isinstance(site.get('colors'),dict):raise ValueError('site.json: colors must be an object')
    for key,color in site['colors'].items():
        if key not in allowed or not isinstance(color,str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',color):
            raise ValueError('site.json: use a six-digit hex color for '+key)
    return {k:site[k] for k in ('name','subtitle','eyebrow','headline','description','footer','colors')}

def prepare(project):
    project=Path(project);brand=engine.read(project/'brand.json');ads=engine.read(project/'ads.json');packs=[]
    for ad in ads:
        pack=dict(ad)
        # Brand facts are shared; students only edit individual creative fields in ads.json.
        pack.update(brand=brand['name'],cta=brand['cta'],destination=brand['destination'],proof=brand['proof'],kind='original',status='draft')
        pack.pop('approval',None);pack.pop('download',None)
        pack['assets']=[]
        for order,name in enumerate(ad.get('images',[]),1):
            p=engine.inside(project/'assets',name);data=p.read_bytes();w,h=engine.png_dimensions(data)
            pack['assets'].append({'path':name,'order':order,'kind':'image','width':w,'height':h,'sha256':engine.digest(data)})
        errors=engine.validate_pack(pack,project/'assets')
        if errors:raise ValueError(ad.get('id','Ad')+': '+'; '.join(errors))
        packs.append(pack)
    references=engine.read(project/'references.json')
    for ref in references:
        if ref.get('kind')!='reference' or ref.get('status')!='reference_only':
            raise ValueError('references.json accepts only reference_only research records')
    return packs,references

def build_project(project,out):
    site=load_site(project);packs,refs=prepare(project)
    result=engine.build(packs+refs,out,Path(project)/'assets')
    engine.write(Path(out)/'site.json',site)
    # Drafts are always rebuilt from inputs. Approval happens later on an explicit pack copy.
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=('preview','build','check','pack','render'))
    p.add_argument('--project',default=str(ROOT/'student'))
    p.add_argument('--out');p.add_argument('--id');p.add_argument('--font');p.add_argument('--port',type=int,default=8767)
    a=p.parse_args()
    try:
        if a.command=='render':
            if not a.font or not a.out:raise ValueError('render requires --font Sarabun.ttf --out NEW-PROJECT')
            from scripts.render_pack import render
            project=Path(a.project);out=Path(a.out)
            if out.exists():raise ValueError('Output exists; choose a new project folder')
            site=load_site(project);brand=engine.read(project/'brand.json');ads=engine.read(project/'ads.json')
            concepts=[dict(ad,brand=brand['name'],cta=brand['cta'],destination=brand['destination'],proof=brand['proof']) for ad in ads]
            out.mkdir(parents=True)
            render(concepts,out/'assets',a.font,site['colors'])
            for ad in ads:ad['images']=[ad['id']+'.png']
            engine.write(out/'ads.json',ads)
            for name in ('site.json','brand.json','watchlist.json','references.json'):shutil.copy2(project/name,out/name)
            print('Rendered new editable project: '+str(out));return 0
        if a.command=='check':
            load_site(a.project);packs,refs=prepare(a.project);print(f'OK: {len(packs)} editable ads, {len(refs)} references');return 0
        if a.command=='pack':
            if not a.id or not a.out:raise ValueError('pack requires --id AD-ID --out NEW-FILE.json')
            packs,_=prepare(a.project);pack=next((x for x in packs if x['id']==a.id),None)
            if not pack:raise ValueError('Unknown ad ID')
            engine.write(a.out,pack);print('Draft pack saved: '+a.out);return 0
        out=Path(a.out) if a.out else ROOT/'builds'/datetime.now().strftime('student-%Y%m%d-%H%M%S-%f')
        result=build_project(a.project,out);print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
        if a.command=='preview':
            handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(out.resolve()))
            with http.server.ThreadingHTTPServer(('127.0.0.1',a.port),handler) as server:
                print(f'Open http://localhost:{a.port} — Ctrl+C to stop. Edit student/ and run preview again to refresh.',flush=True)
                try:server.serve_forever()
                except KeyboardInterrupt:pass
        return 0
    except (ValueError,KeyError,OSError,json.JSONDecodeError) as e:
        print('Check your student files: '+str(e),file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
