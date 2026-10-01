"""Research-informed slanted, round-section pegboard key hook. Units mm.
Product mounting angles are not published: this is our dimensioned adaptation.
"""
from pathlib import Path
import numpy as np,math,json
from shapely.geometry import LineString,box,Point,Polygon
from shapely.ops import unary_union
import shapely,trimesh
from collections import deque
OUT=Path(__file__).resolve().parent;OUT.mkdir(exist_ok=True)

HOLE_D=6.25;BOARD_T=6.55;GAP=6.70;RADIUS=2.4;TIP_ANGLE=60
ZC=2.9;FLOOR=.9;HEIGHT=5.3

def tube_samples(angle):
 centers=[(x,0,2.4) for x in np.linspace(3,-GAP,40)]
 rad=3.0;aa=math.radians(angle)
 centers += [(-GAP-rad*math.sin(a),rad-rad*math.cos(a),2.4) for a in np.linspace(0,aa,25)[1:]]
 endx,endy,_=centers[-1]
 centers += [(endx-l*math.cos(aa),endy+l*math.sin(aa),2.4-.7*(l/3)) for l in np.linspace(0,3,20)[1:]]
 return centers

def pin_samples():
 return [(x,-25.4+max(0,-x)*math.tan(math.radians(3)),2.8 if x>=-2.8 else 2.8-1.0*((-x-2.8)/2.0)) for x in np.linspace(3,-4.8,32)]

def footprint(samples,dz=0):
 circles=[Point(x,y).buffer(math.sqrt(max(0,r*r-dz*dz)),quad_segs=10) if abs(dz)<r else None for x,y,r in samples]
 # Convex hulls between consecutive circular sections preserve taper continuity.
 segments=[unary_union([a,b]).convex_hull for a,b in zip(circles,circles[1:]) if a is not None and b is not None]
 pieces=[g for g in circles if g is not None]+segments
 return unary_union(pieces)

def body_shape():
 c=[(3,-17),(12,-17)]+[(12+4*math.cos(a),-13+4*math.sin(a)) for a in np.linspace(-math.pi/2,0,24)[1:]]+[(16,-10)]
 return unary_union([box(.2,-30,5.3,-.5),LineString(c).buffer(2.2,quad_segs=12,cap_style='round')])
BODY=body_shape()

def obstacles(half):
 return unary_union([box(-BOARD_T,-100,-.001,-25.4-half),box(-BOARD_T,-25.4+half,-.001,-half),box(-BOARD_T,half,-.001,100)])
SLAB=box(-BOARD_T,-100,-.001,100)

def transformed(g,deg,x,y):
 a=math.radians(deg);c,s=math.cos(a),math.sin(a)
 return shapely.transform(g,lambda p: np.column_stack((p[:,0]*c-p[:,1]*s+x,p[:,0]*s+p[:,1]*c+y)))

def path_search(upper,lower,check_bands):
 hook=unary_union([upper,lower,BODY]);coords=np.array(hook.exterior.coords);bodycoords=np.array(BODY.exterior.coords)
 xs=np.arange(0,26.01,.25);ys=np.arange(-5,10.01,.25);angles=np.arange(0,75.01,2.5)
 offsets=np.array([(x,y) for x in xs for y in ys]);valid=[];outside=[];obs=obstacles(HOLE_D/2).buffer(.06)
 for deg in angles:
  a=math.radians(deg);c,s=math.cos(a),math.sin(a)
  q=np.column_stack((coords[:,0]*c-coords[:,1]*s,coords[:,0]*s+coords[:,1]*c))
  b=np.column_stack((bodycoords[:,0]*c-bodycoords[:,1]*s,bodycoords[:,0]*s+bodycoords[:,1]*c))
  geoms=shapely.polygons(q[None,:,:]+offsets[:,None,:]);bg=shapely.polygons(b[None,:,:]+offsets[:,None,:])
  ok=(~shapely.intersects(geoms,obs)&~shapely.intersects(bg,SLAB))
  for z0,z1,g,band_obs in check_bands:
   bc=np.array(g.exterior.coords);bq=np.column_stack((bc[:,0]*c-bc[:,1]*s,bc[:,0]*s+bc[:,1]*c))
   ok &= ~shapely.intersects(shapely.polygons(bq[None,:,:]+offsets[:,None,:]),band_obs.buffer(.06))
  valid.append(ok.reshape(len(xs),len(ys)))
  outside.append((offsets[:,0]+q[:,0].min()>.15).reshape(len(xs),len(ys)))
 valid=np.array(valid);outside=np.array(outside);start=(0,0,int(np.argmin(abs(ys))))
 assert valid[start], 'Final seating collides'
 queue=deque([start]);prev={start:None};end=None
 while queue:
  st=queue.popleft()
  if outside[st]:end=st;break
  for dim in range(3):
   for sign in [-1,1]:
    nxt=list(st);nxt[dim]+=sign;nxt=tuple(nxt)
    if any(nxt[k]<0 or nxt[k]>=valid.shape[k] for k in range(3)) or not valid[nxt] or nxt in prev:continue
    prev[nxt]=st;queue.append(nxt)
 if end is None:return None
 path=[]
 while end is not None:
  a,x,y=end;path.append([float(angles[a]),float(xs[x]),float(ys[y])]);end=prev[end]
 return path

def create(angle):
 global TIP_ANGLE
 TIP_ANGLE=angle
 u=tube_samples(angle);l=pin_samples();up=footprint(u);lo=footprint(l)
 # Build a flat-bottom approximation of round sections in 0.1 mm bands.
 # All exported profiles are checked against the strictest opening over the band.
 bands=[]
 for z0,z1 in zip(np.arange(FLOOR,HEIGHT,.1),np.arange(FLOOR+.1,HEIGHT+.001,.1)):
  z0,z1=round(z0,5),round(z1,5);dz=min(abs(z0-ZC),abs(z1-ZC)) if not z0<=ZC<=z1 else 0
  upper=footprint(u,dz);lower=footprint(l,dz)
  g=unary_union([upper,lower,BODY]);g=g.buffer(0)
  strict_dz=max(abs(z0-ZC),abs(z1+.005-ZC));half=math.sqrt((HOLE_D/2)**2-strict_dz**2)
  bands.append((z0,z1,g,obstacles(half)))
 # We approximate circles and hold each band at its widest profile; test exact stack.
 checked_indices={0,len(bands)-1,10,20,30,35}
 for attempt in range(12):
  path=path_search(up,lo,[bands[i] for i in sorted(checked_indices)])
  if path is None:return None
  collision=None
  for a,b in zip(path,path[1:]):
   for t in np.linspace(0,1,5):
    pose=np.array(a)*(1-t)+np.array(b)*t
    for i,(z0,z1,g,obs) in enumerate(bands):
     if transformed(g,*pose).intersects(obs):collision=i;break
    if collision is not None:break
   if collision is not None:break
  if collision is None:break
  if collision in checked_indices:return ('between_grid_collision',pose.tolist(),bands[collision][0])
  checked_indices.add(collision)
 else:return ('search_limit',sorted(checked_indices))
 poses=[]
 for a,b in zip(path,path[1:]):
  poses.extend((np.array(a)*(1-t)+np.array(b)*t).tolist() for t in np.linspace(0,1,11))
 minclear=100;rear=0
 for pose in poses:
  for z0,z1,g,obs in bands:
   q=transformed(g,*pose)
   if q.intersects(obs):return ('band_collision',pose,z0)
   minclear=min(minclear,q.distance(obs));rear=max(rear,-q.bounds[0]-BOARD_T)
  assert not transformed(BODY,*pose).intersects(SLAB)
 # Union extruded slabs to one solid. Tiny overlap handles floating point coplanarity.
 meshes=[]
 for z0,z1,g,obs in bands:
  mesh=trimesh.creation.extrude_polygon(g,height=z1-z0+.005,engine='earcut');mesh.apply_translation([0,0,z0]);meshes.append(mesh)
 mesh=trimesh.boolean.union(meshes,engine='manifold')
 assert np.isfinite(mesh.vertices).all() and mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
 # Neck is locally round with a flat printing floor, not a thin rectangular plate.
 mesh.apply_translation([-mesh.bounds[0,0],-mesh.bounds[0,1],-FLOOR])
 mesh.export(OUT/'pegboard-design-1.stl',file_type='stl_ascii')
 report=dict(peg_diameter_mm=4.8,tip_diameter_mm=3.4,tip_angle_above_rearward_horizontal_degrees=angle,board_gap_mm=GAP,lower_pin_diameter_mm=5.6,lower_pin_reach_mm=4.8,lower_pin_angle_degrees=3,hole_center_spacing_mm=25.4,front_projection_mm=18.2,body_print_depth_mm=HEIGHT-FLOOR,flat_floor_z_mm=FLOOR,modeled_board_thickness_mm=BOARD_T,modeled_hole_diameter_mm=HOLE_D,slice_bands=len(bands),verified_poses=len(poses),minimum_modeled_clearance_mm=minclear,required_rear_clearance_mm=rear,insertion_path=path,upper_centerline=u,lower_centerline=l,upper_outline=list(map(list,up.exterior.coords)),lower_outline=list(map(list,lo.exterior.coords)),body_outline=list(map(list,BODY.exterior.coords)),dimensions_mm=mesh.extents.tolist(),volume_mm3=float(mesh.volume),watertight=True,consistent_winding=True)

 parents=list(range(len(mesh.vertices)))
 def root(v):
  while parents[v]!=v:parents[v]=parents[parents[v]];v=parents[v]
  return v
 for a,b in mesh.edges:
  ra,rb=root(a),root(b)
  if ra!=rb:parents[ra]=rb
 components=len({root(i) for i in range(len(mesh.vertices))});assert components==1
 points=np.array(report['body_outline']+report['upper_outline']+report['lower_outline'])
 radius=np.linalg.norm(points,axis=1).max()
 bound=max(.025/2,2*radius*np.sin(np.radians(.25/2)/2))
 report.update(connected_components=components,triangle_count=len(mesh.faces),exported_mesh_height_mm=float(mesh.extents[2]),mesh_euler_number=mesh.euler_number,maximum_half_step_motion_bound_mm=float(bound),clearance_after_between_sample_motion_bound_mm=float(minclear-bound))
 assert report['clearance_after_between_sample_motion_bound_mm']>0
 (OUT/'geometry-and-motion-check.json').write_text(json.dumps(report,indent=2))
 # The editable source reproduces the exact banded geometry.
 scad=['// V4 prototype. mm. Flat-side down.','union(){']
 for z0,z1,g,obs in bands:
  scad.append('translate([0,0,'+str(z0-FLOOR)+']) linear_extrude(height='+str(z1-z0+.005)+') polygon(points='+json.dumps(list(map(list,g.exterior.coords)))+');')
 scad.append('}')
 (OUT/'pegboard-design-1.scad').write_text('\n'.join(scad))
 return report

if __name__=='__main__':
 for angle in [45,30]:
  print('Checking tip angle',angle,flush=True);result=create(angle)
  if isinstance(result,dict):print('PASS',angle,result['verified_poses'],'poses',result['minimum_modeled_clearance_mm'],'clearance',flush=True);break
  print('Not passed:',result,flush=True)
 else:raise RuntimeError('No candidate passes the checked insertion motion')
