"""Keep the V2 upper attachment; add a wider front key hook. Units: mm."""
from pathlib import Path
# Load only the existing imports/functions, without rerunning V2 generation.
exec(Path('work/design_hook_v2.py').read_text().split('\nreports={}')[0])
OUT=Path('outputs/pegboard-key-hooks-v3');OUT.mkdir(exist_ok=True)
old=json.loads(Path('outputs/airgradient-mount-v2/geometry-and-motion-check.json').read_text())
def connected(mesh):
 adjacent={i:set() for i in range(len(mesh.vertices))}
 for face in mesh.faces:
  for a,b in zip(face,np.roll(face,-1)):adjacent[int(a)].add(int(b));adjacent[int(b)].add(int(a))
 seen={0};stack=[0]
 while stack:
  for n in adjacent[stack.pop()]-seen:seen.add(n);stack.append(n)
 return len(seen)==len(mesh.vertices)
reports={}
for label,w in [('A',2.0),('B',2.4)]:
 original=shape(w)
 # J-shaped key hook, facing away from the board. 4.6 mm arm profile.
 center=[(3,-18),(14,-18)]+[(14+4*math.cos(a),-14+4*math.sin(a)) for a in np.linspace(-math.pi/2,0,25)[1:]]+[(18,-11)]
 arm=LineString(center).buffer(2.3,quad_segs=12,cap_style='round')
 p=unary_union([original,box(.3,-23,6,-5),arm])
 for cx in ([3.15] if label=='A' else [2.0,4.3]):p=p.difference(Point(cx,-23).buffer(.65,quad_segs=8))
 thick=p.intersection(box(-50,-50,50,-5))
 assert p.intersection(box(-50,-5,50,50)).symmetric_difference(original.intersection(box(-50,-5,50,50))).area<1e-9
 # Check the exact saved insertion path against the entire updated object.
 half=math.sqrt(3**2-(w/2)**2)
 obstacles=unary_union([box(-6.6,-100,-.001,-half),box(-6.6,half,-.001,100)])
 slab=box(-6.6,-100,-.001,100)
 coords=np.array(p.exterior.coords);extra=np.array(thick.exterior.coords);count=0;rear=0;clearance=100
 states=old[label]['insertion_path']
 for start,end in zip(states,states[1:]):
  for u in np.linspace(0,1,21):
   deg,x,y=np.array(start)*(1-u)+np.array(end)*u;a=math.radians(deg)
   rot=np.array([[math.cos(a),math.sin(a)],[-math.sin(a),math.cos(a)]])
   q=Polygon(coords@rot+[x,y]);e=Polygon(extra@rot+[x,y])
   assert not q.intersects(obstacles),'Main profile collides'
   assert not e.intersects(slab),'Thickened front body collides with board'
   count+=1;rear=max(rear,-q.bounds[0]-6.6);clearance=min(clearance,q.distance(obstacles))
 base=trimesh.creation.extrude_polygon(p,height=w,engine='earcut')
 # Overlap by 0.1 mm before the Boolean union to avoid touching-shell ambiguity.
 raised=trimesh.creation.extrude_polygon(thick,height=6-w+.1,engine='earcut');raised.apply_translation([0,0,w-.1])
 mesh=trimesh.boolean.union([base,raised],engine='manifold')
 assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0 and connected(mesh)
 mesh.apply_translation([-mesh.bounds[0,0],-mesh.bounds[0,1],0])
 name=f'{label}-key-hook-{w:.1f}mm-attachment'
 mesh.export(OUT/(name+'.stl'),file_type='stl_ascii')
 def poly(g):return 'polygon(points='+json.dumps(list(map(list,g.exterior.coords)))+');'
 (OUT/(name+'.scad')).write_text('// Experimental key hook. Side-down print. mm. No verified load rating.\nunion(){\nlinear_extrude(height='+str(w)+') '+poly(p)+'\ntranslate([0,0,'+str(w-.1)+']) linear_extrude(height='+str(6-w+.1)+') '+poly(thick)+'\n}\n')
 reports[label]=dict(upper_attachment_unchanged=True,front_body_depth_mm=6,attachment_section_mm=w,outline=list(map(list,p.exterior.coords)),thick_outline=list(map(list,thick.exterior.coords)),insertion_path=states,verified_sampled_poses=count,minimum_obstacle_clearance_mm=clearance,required_rear_clearance_mm=rear,watertight=bool(mesh.is_watertight),single_connected_solid=True,volume_mm3=float(mesh.volume),dimensions_mm=mesh.extents.tolist(),assumed_board_thickness_mm=6.6,assumed_hole_diameter_mm=6.0)
 print(label,'verified',count,'poses; dimensions',mesh.extents.tolist(),flush=True)
(OUT/'geometry-and-motion-check.json').write_text(json.dumps(reports,indent=2))
