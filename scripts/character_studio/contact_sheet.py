#!/usr/bin/env python3
"""Place actual delivered-GLB renders side by side without rescaling pixels.
Requires Pillow. --font accepts a local CJK font; otherwise English labels.
"""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--outputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--font',type=Path)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    reports={cid:json.loads((args.outputs/cid/'report.json').read_text()) for cid in ('d03','d06')}
    versions={r['version'] for r in reports.values()}
    if len(versions)!=1:raise ValueError('Both compared candidates must belong to the same studio version')
    version=versions.pop()
    cjk=bool(args.font)
    fontpath=str(args.font) if args.font else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font=lambda size:ImageFont.truetype(fontpath,size)
    metadata={'schema_version':1,'source':'actual exported GLB reimported into Blender','pixels_rescaled':False,'images':[]}
    for view,h,title,sub in [
      ('front',1000,'同尺度全身灰模' if cjk else 'Same-scale gray bodies','共同地面與 2.20 m 正交尺度' if cjk else 'Shared ground and 2.20 m orthographic scale'),
      ('face',800,'無髮臉部灰模' if cjk else 'Hairless gray faces','相同 0.38 m 正交尺度，分別對準頭部' if cjk else 'Equal 0.38 m scale, camera centered on each head'),
      ('face_threequarter',800,'無髮臉部・35°' if cjk else 'Hairless faces, 35 degrees','相同鏡頭尺度與燈光；未使用皮膚法線' if cjk else 'Equal camera scale and light; no skin normal textures')]:
        canvas=Image.new('RGB',(1648,h+222),(26,32,35));draw=ImageDraw.Draw(canvas)
        draw.text((24,15),title,font=font(36),fill=(240,244,240))
        draw.text((24,65),'D03 / D06  |  '+version+'  |  '+sub,font=font(21),fill=(181,195,189))
        records=[]
        for i,cid in enumerate(('d03','d06')):
            source=args.outputs/cid/'renders'/f'{cid}_delivered_{view}.png'
            image=Image.open(source).convert('RGB')
            if image.size!=(800,h):raise ValueError('Expected original unscaled review dimensions')
            x=16+i*816;canvas.paste(image,(x,145))
            label=(('D03 高瘦青年・24 歲・設計 186 cm','D06 較豐滿高齡女性・73 歲・設計 153 cm')[i] if cjk else ('D03 | Young slender man | 24 | 186 cm','D06 | Older fuller woman | 73 | 153 cm')[i])
            draw.text((x+8,104),label,font=font(24),fill=(238,239,235))
            records.append({'file':str(source.relative_to(args.outputs)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_dimensions':list(image.size)})
        note='實際模型渲染／灰模候選，尚未通過完整美術與動作驗收' if cjk else 'Actual GLB renders. Gray candidates; complete appearance and motion acceptance remains open.'
        draw.text((24,h+165),note,font=font(22),fill=(181,195,189))
        target=args.out/f'studio_{version}_{view}_comparison.png';canvas.save(target)
        metadata['images'].append({'file':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'sources':records})
    (args.out/'comparison_image_provenance.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
