import numpy as np, shapely, json, math
from shapely.geometry import LineString, box, Polygon, Point
from shapely.ops import unary_union
from pathlib import Path
from collections import deque
import trimesh
OUT=Path('outputs/airgradient-mount-v2');OUT.mkdir(exist_ok=True)

def shape(w):
 # Horizontal neck, generous smooth bend, upright tip; all dimensions mm.
 # Positive x is in front of the board; y is upward when installed.
 path=[(2,0),(-8,0)]+[(-8-3*math.sin(a),3-3*math.cos(a)) for a in np.linspace(0,math.pi/2,25)[1:]]+[(-11,5)]
 tube=LineString(path).buffer(w/2,quad_segs=8,cap_style='round')
 tab=box(.3,-17,6,2)
 return unary_union([tube,tab])

def find_path(poly,w):
 # Conservative board envelope: thicker and smaller holes than nominal.
 half=math.sqrt(3**2-(w/2)**2)
 obstacles=unary_union([box(-6.6,-100,-.001,-half),box(-6.6,half,-.001,100)])
 coords=np.array(poly.exterior.coords)
 xs=np.arange(-1,32.01,.25);ys=np.arange(-20,20.01,.25);angles=np.arange(0,120.01,2)
 offsets=np.array([(x,y) for x in xs for y in ys]);valid=[];outside=[]
 for deg in angles:
  a=math.radians(deg);r=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
  q=coords@r.T
  polygons=shapely.polygons(q[None,:,:]+offsets[:,None,:])
  valid.append((~shapely.intersects(polygons,obstacles)).reshape(len(xs),len(ys)))
  outside.append((offsets[:,0]+q[:,0].min()>.25).reshape(len(xs),len(ys)))
 valid=np.array(valid);outside=np.array(outside)
 start=(0,int(np.argmin(abs(xs))),int(np.argmin(abs(ys))))
 assert valid[start], 'seated collision'
 queue=deque([start]);parent={start:None};end=None
 while queue:
  s=queue.popleft()
  if outside[s]:end=s;break
  for dim in range(3):
   for sign in (-1,1):
    n=list(s);n[dim]+=sign;n=tuple(n)
    if any(n[k]<0 or n[k]>=valid.shape[k] for k in range(3)) or not valid[n] or n in parent:continue
    parent[n]=s;queue.append(n)
 if end is None:raise RuntimeError('No insertion path')
 states=[]
 while end is not None:
  a,x,y=end;states.append([float(angles[a]),float(xs[x]),float(ys[y])]);end=parent[end]
 # states run outside -> installed, verify intermediate continuous steps finely.
 checked=0;rear=0;clearance=100
 for s,t in zip(states,states[1:]):
  for u in np.linspace(0,1,21):
   deg,x,y=np.array(s)*(1-u)+np.array(t)*u;a=math.radians(deg)
   q=coords@np.array([[math.cos(a),math.sin(a)],[-math.sin(a),math.cos(a)]])+[x,y]
   g=Polygon(q)
   if g.intersects(obstacles):raise RuntimeError('Intermediate collision')
   checked+=1;rear=max(rear,-q[:,0].min()-6.6);clearance=min(clearance,g.distance(obstacles))
 return dict(assumed_board_thickness_mm=6.6,assumed_hole_diameter_mm=6.0,cross_section_width_mm=w,verified_sampled_poses=checked,minimum_obstacle_clearance_mm=clearance,required_rear_clearance_mm=rear,insertion_path=states)

reports={}
for w,label in [(2.0,'A'),(2.4,'B')]:
 p=shape(w)
 for cx in ([3.15] if label=='A' else [2.0,4.3]): p=p.difference(Point(cx,-17).buffer(.65,quad_segs=8))
 report=find_path(p,w)
 mesh=trimesh.creation.extrude_polygon(p,height=w,engine='earcut');mesh.apply_translation([-mesh.bounds[0,0],-mesh.bounds[0,1],0]);assert mesh.is_watertight and mesh.volume>0
 name=f'{label}-smooth-hook-{w:.1f}mm'
 mesh.export(OUT/(name+'.stl'),file_type='stl_ascii')
 (OUT/(name+'.scad')).write_text('// Unloaded fit test; side-down print. Original coordinates, mm.\nlinear_extrude(height='+str(w)+') polygon(points='+json.dumps(list(map(list,p.exterior.coords)))+');\n')
 report.update(watertight=bool(mesh.is_watertight),volume_mm3=float(mesh.volume),dimensions_mm=mesh.extents.tolist(),outline=list(map(list,p.exterior.coords)))
 reports[label]=report;print(label,'path passed',len(report['insertion_path']),'poses',report['verified_sampled_poses'],'rear clearance',report['required_rear_clearance_mm'],flush=True)
(OUT/'geometry-and-motion-check.json').write_text(json.dumps(reports,indent=2))
