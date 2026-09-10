"""Render original typography-led PNG ads with a supplied Sarabun font. No paid API."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import read,write,digest,safe_id
def render(concepts,out,font):
    from PIL import Image,ImageDraw,ImageFont
    out=Path(out);out.mkdir(parents=True,exist_ok=False);packs=[]
    for c in concepts:
        safe_id(c['id']);image=Image.new('RGB',(1080,1350),'#17181a');d=ImageDraw.Draw(image)
        small=ImageFont.truetype(str(font),34);body=ImageFont.truetype(str(font),44);large=ImageFont.truetype(str(font),78)
        d.text((80,90),c['brand'],font=small,fill='#e2d7c8');d.line((80,165,1000,165),fill='#94764a',width=3)
        # Wrap by measured width, including Thai without spaces. Layout is verified before writing.
        lines=[];current=''
        for ch in c['headline']:
            if ch=='\n' or d.textlength(current+ch,font=large)>900:
                lines.append(current);current='' if ch=='\n' else ch
            else:current+=ch
        if current:lines.append(current)
        if len(lines)>7:raise ValueError('Headline too long for readable template: '+c['id'])
        for i,line in enumerate(lines):d.text((80,265+i*110),line,font=large,fill='#e2d7c8')
        if d.textlength(c['cta'],font=body)>870:raise ValueError('CTA too long')
        d.rounded_rectangle((80,1090,1000,1220),radius=12,fill='#94764a');d.text((115,1120),c['cta'],font=body,fill='white')
        if c.get('demo'):d.text((80,1260),'ตัวอย่างสำหรับฝึกใช้งาน',font=small,fill='#e2d7c8')
        target=out/(c['id']+'.png');image.save(target)
        pack=dict(c);pack['assets']=[{'path':target.name,'kind':'image','order':1,'width':1080,'height':1350,'sha256':digest(target.read_bytes())}]
        pack['status']='draft';pack.pop('approval',None);pack['rights']='owned';pack['rights_evidence']='Original typography layout rendered from supplied brand copy; reviewer must verify copy rights and claims.'
        write(out/(c['id']+'.json'),pack);packs.append(pack)
    write(out/'catalog.json',packs);return packs
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--concepts',required=True);p.add_argument('--out',required=True);p.add_argument('--font',required=True);a=p.parse_args();render(read(a.concepts),a.out,a.font)
