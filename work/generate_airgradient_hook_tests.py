"""Dependency-free, closed-solid pegboard hook fit coupons; dimensions in mm."""
from pathlib import Path
import math, struct, json, zipfile
from collections import Counter

OUT = Path(__file__).resolve().parents[1] / 'outputs/airgradient-mount-v1'
OUT.mkdir(parents=True, exist_ok=True)

def cross(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

def triangles(p):
    ids=list(range(len(p))); result=[]
    while len(ids)>3:
        for i,b in enumerate(ids):
            a,c=ids[i-1],ids[(i+1)%len(ids)]
            if cross(p[a],p[b],p[c])<=1e-9: continue
            if any(all(cross(p[u],p[v],p[q])>=-1e-9 for u,v in [(a,b),(b,c),(c,a)]) for q in ids if q not in (a,b,c)): continue
            result.append((a,b,c)); ids.pop(i); break
        else: raise ValueError('Cannot triangulate polygon')
    return result+[tuple(ids)]

def coupon(board):
    gap=board+0.4; tip=-gap-3.6
    # Board face x=0, hooks extend toward negative x, vertical axis is y.
    # Small chamfers at free tips aid insertion. Single continuous solid.
    p=[(0,-31),(5,-31),(5,10),(0,10),(0,1.8),
       (-gap,1.8),(-gap,7.0),(-gap-.8,7.8),(tip+.8,7.8),
       (tip,7.0),(tip,-1.0),(tip+.8,-1.8),(0,-1.8),
       (0,-23.6),(-gap-.2,-23.6),(-gap-1,-24.4),
       (-gap-1,-26.4),(-gap-.2,-27.2),(0,-27.2)]
    assert sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))>0
    n=len(p); cap=triangles(p)
    v=[(x-tip,y+31,z) for z in [0,3.6] for x,y in p]
    f=[(c,b,a) for a,b,c in cap]+[(a+n,b+n,c+n) for a,b,c in cap]
    for a in range(n):
        b=(a+1)%n; f.extend([(a,b,b+n),(a,b+n,a+n)])
    return p,v,f

def validate(v,f):
    edges=Counter(tuple(sorted((a,b))) for face in f for a,b in zip(face,face[1:]+face[:1]))
    assert set(edges.values())=={2}
    directed=Counter((a,b) for face in f for a,b in zip(face,face[1:]+face[:1]))
    assert all(directed[(b,a)]==1 for a,b in directed)
    volume=0
    for a,b,c in f:
        a,b,c=v[a],v[b],v[c]
        volume+=sum(a[i]*(b[(i+1)%3]*c[(i+2)%3]-b[(i+2)%3]*c[(i+1)%3]) for i in range(3))/6
    assert volume>0
    return {'closed_manifold':True,'volume_mm3':round(volume,2),'solid_PLA_mass_g_at_1_24':round(volume*.00124,2),'dimensions_mm':[round(max(a[i] for a in v)-min(a[i] for a in v),2) for i in range(3)]}

def stl(path,v,f):
    with path.open('wb') as h:
        h.write(b'AirGradient pegboard FIT TEST ONLY; mm'.ljust(80,b' ')); h.write(struct.pack('<I',len(f)))
        for a,b,c in f:
            h.write(struct.pack('<12fH',0,0,0,*v[a],*v[b],*v[c],0))

reports={}; models=[]
for index,board in enumerate([3.2,4.8,6.4]):
    p,v,f=coupon(board); name=f'hook-test-board-{board:.1f}mm'
    stl(OUT/(name+'.stl'),v,f); reports[name]=validate(v,f); models.append((v,f))
    source='// Fit coupon only, not a rated hanger. Side-down print orientation.\n'
    source+='// Intended board thickness %.1f mm; gap includes 0.4 mm clearance.\n'%board
    source+='linear_extrude(height=3.6) polygon(points='+json.dumps(p)+');\n'
    (OUT/(name+'.scad')).write_text(source)

# Generic model-only 3MF; deliberately no printer, filament, or slicing presets.
resources=[]; build=[]
for i,(v,f) in enumerate(models,1):
    vertices=''.join(f'<vertex x="{x}" y="{y}" z="{z}"/>' for x,y,z in v)
    faces=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in f)
    resources.append(f'<object id="{i}" type="model" name="Board {[3.2,4.8,6.4][i-1]} mm"><mesh><vertices>{vertices}</vertices><triangles>{faces}</triangles></mesh></object>')
    build.append(f'<item objectid="{i}" transform="1 0 0 0 1 0 0 0 1 {(i-1)*28} 0 0"/>')
model='<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>'+''.join(resources)+'</resources><build>'+''.join(build)+'</build></model>'
with zipfile.ZipFile(OUT/'hook-tests-all-three.3mf','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    z.writestr('3D/3dmodel.model',model)
(OUT/'mesh-validation.json').write_text(json.dumps(reports,indent=2))
print(json.dumps(reports,indent=2))
