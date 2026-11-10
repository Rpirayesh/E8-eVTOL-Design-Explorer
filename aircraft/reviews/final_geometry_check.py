"""Independent final geometry/export review using FreeCAD's STEP importer.
No regeneration or source edits. Geometry verification is not flight validation.
"""
from pathlib import Path
import sys,json,math,struct,os,hashlib
ROOT=Path(__file__).resolve().parents[1]
for p in ['/usr/lib/freecad-python3/lib','/usr/lib/freecad/lib']:
    if Path(p).exists():sys.path.append(p)
import FreeCAD as App,Part,Import

def leaves(doc):
    return {o.Label:o.Shape for o in doc.Objects if o.TypeId in ['Part::Feature','PartDesign::Feature'] and not o.Shape.isNull()}
def bb(shape):
    b=shape.BoundBox
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def combined_bb(shapes):
    boxes=[bb(s) for s in shapes]
    return [min(b[k] for b in boxes) for k in range(3)]+[max(b[k] for b in boxes) for k in range(3,6)]
def touching(a,b):
    return dict(distance_mm=a.distToShape(b)[0],intersection_mm3=a.common(b).Volume)
def overlap_box(a,b):
    return not(a.XMax<b.XMin or a.XMin>b.XMax or a.YMax<b.YMin or a.YMin>b.YMax or a.ZMax<b.ZMin or a.ZMin>b.ZMax)
def stl(path):
    data=path.read_bytes();n=struct.unpack('<I',data[80:84])[0];pts=[];bad=0
    for i in range(n):
        t=struct.unpack('<12fH',data[84+i*50:134+i*50]);v=[t[j:j+3] for j in [3,6,9]];pts+=v
        if not all(math.isfinite(x) for p in v for x in p):bad+=1
    return dict(triangles=n,actual_bytes=len(data),expected_bytes=84+50*n,nonfinite_triangles=bad,
                bbox_mm=[min(p[k] for p in pts) for k in range(3)]+[max(p[k] for p in pts) for k in range(3)])

def main():
    os.write(1,b'REVIEW START\n')
    p=json.loads((ROOT/'selected_design.json').read_text());exports={}
    for filename in ['E8_Winged_Hover.step','E8_Winged_Cruise.step','E8_Wingless_Hover.step']:
        os.write(1,('EXPORT '+filename+'\n').encode())
        d=App.newDocument('G'+str(len(exports)));Import.insert(str(ROOT/'cad'/filename),d.Name);d.recompute();shapes=leaves(d)
        exports[filename]=dict(leaf_count=len(shapes),solids=sum(len(s.Solids) for s in shapes.values()),
            invalid=[k for k,v in shapes.items() if not v.isValid()],bbox_mm=combined_bb(shapes.values()))
        if filename=='E8_Winged_Hover.step':
            hover_hull_volume=shapes['Fuselage_shell_envelope_15mm_not_laminate'].Volume
        App.closeDocument(d.Name)
        os.write(1,b'EXPORT DONE\n')
    d=App.openDocument(str(ROOT/'cad'/'E8_Concept_Assembly.FCStd'));shapes=leaves(d)
    os.write(1,b'NATIVE OPEN\n')
    exports['E8_Concept_Assembly.FCStd']=dict(leaf_count=len(shapes),solids=sum(len(s.Solids) for s in shapes.values()),
        invalid=[k for k,v in shapes.items() if not v.isValid()],bbox_mm=combined_bb(shapes.values()))
    spar=shapes['Main_spar_homogeneous_box_assumption']
    seats={k:touching(spar,v) for k,v in shapes.items() if k.startswith('Seat_')}
    attachments={}
    for i in range(1,9):
        names={k:v for k,v in shapes.items() if k.startswith(f'R{i}_')}
        hub=names[f'R{i}_hub'];motor=names[f'R{i}_motor_REB50_envelope'];axle=names[f'R{i}_tilt_axle']
        yoke=names.get(f'R{i}_rotating_yoke_envelope')
        standoff=names[f'R{i}_standoff']
        attachments[str(i)]=dict(blade_hub={k:touching(v,hub) for k,v in names.items() if 'blade_' in k},
            yoke_motor=touching(yoke,motor) if yoke else None,yoke_axle=touching(yoke,axle) if yoke else None,
            standoff_fixed_part_distances_mm={k:standoff.distToShape(v)[0] for k,v in names.items() if any(x in k for x in ['fork','axle','crosshead'])},
            standoff_boom=touching(standoff,shapes['Longitudinal_boom_'+('-1' if i%2 else '1')]))
    pylons={}
    fixed_rotor_names=[k for k in shapes if '_blade_' in k or '_hub' in k or '_motor_' in k or '_rotating_yoke_' in k]
    fixed={k:v for k,v in shapes.items() if k not in fixed_rotor_names}
    for name,shape in shapes.items():
        if name.startswith('High_wing_pylon_'):
            near={k:shape.distToShape(v)[0] for k,v in fixed.items() if k!=name and not k.startswith(('Wing_','Aileron_','Main_spar','High_wing_pylon'))}
            pylons[name]=dict(nearest_lower_or_other_part=sorted(near.items(),key=lambda kv:kv[1])[:6])
    disk_events=[];swept_rotor_events=[]
    for i,(xm,ym) in enumerate([(x,y) for x in p['rotor_rows_x_m'] for y in [-p['rotor_y_m'],p['rotor_y_m']]],1):
        pivot=App.Vector(xm*1000,ym*1000,p['rotor_hub_z_m']*1000-400)
        for deg in range(0,91,5):
            theta=math.radians(deg);axis=App.Vector(-math.sin(theta),0,math.cos(theta));hub=pivot+axis*400
            disk=Part.makeCylinder(p['rotor_diameter_m']*500,20,hub-axis*10,axis)
            for name,shape in fixed.items():
                if not overlap_box(disk.BoundBox,shape.BoundBox):continue
                vol=disk.common(shape).Volume
                if vol>1e-3:disk_events.append(dict(rotor=i,tilt_deg=deg,part=name,volume_mm3=vol))
            moving_names=[f'R{i}_motor_REB50_envelope',f'R{i}_rotating_yoke_envelope']
            for moving_name in moving_names:
                mov=shapes[moving_name].copy();mov.rotate(pivot,App.Vector(0,1,0),-deg)
                for name,shape in fixed.items():
                    if name==f'R{i}_tilt_axle':continue # intended revolute interface
                    if not overlap_box(mov.BoundBox,shape.BoundBox):continue
                    vol=mov.common(shape).Volume
                    if vol>1e-3:swept_rotor_events.append(dict(rotor=i,tilt_deg=deg,moving=moving_name,part=name,volume_mm3=vol))
    result=dict(exports=exports,stls={name:stl(ROOT/'cad'/name) for name in ['E8_Winged_Hover.stl','E8_Wingless_Hover.stl']},
        seat_spar=seats,rotor_attachments=attachments,high_wing_pylons=pylons,
        rigid_disk_sweep=dict(tilts_deg=list(range(0,91,5)),rotors=8,collision_events=disk_events,
            definition='20mm-thick rigid disk against fixed shapes; excludes rotating blades, hubs, motor and yoke'),
        motor_yoke_sweep=dict(tilts_deg=list(range(0,91,5)),collision_events=swept_rotor_events,
            exclusions='The own tilt axle is the intended revolute interface'),
        limits='No deformation, tolerances, running blade deflection, bearing/joint design, full pairwise assembly test or dynamic flight validation')
    hull=shapes['Fuselage_shell_envelope_15mm_not_laminate']
    result['battery_hull_intersections_mm3']={name:shape.common(hull).Volume for name,shape in shapes.items()
        if name.startswith('Battery_module_') and not name.endswith('_tray')}
    result['battery_bay_clearance_mm']={name:shape.distToShape(hull)[0] for name,shape in shapes.items()
        if name.startswith('Battery_module_') and not name.endswith('_tray')}
    result['native_step_hull_volume_match_mm3']=abs(hull.Volume-hover_hull_volume)
    result['input_sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
        ['cad/E8_Winged_Hover.step','cad/E8_Winged_Cruise.step','cad/E8_Wingless_Hover.step',
         'cad/E8_Winged_Hover.stl','cad/E8_Wingless_Hover.stl','cad/E8_Concept_Assembly.FCStd',
         'selected_design.json','viewer/E8_3D_Viewer_Offline.html']}
    (ROOT/'reviews'/'geometry_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(exports=exports,seat_spar=seats,rotor1_attachments=attachments['1'],pylons=pylons,
         disk_collision_count=len(disk_events),motor_yoke_collision_count=len(swept_rotor_events)),indent=2))
if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        os.write(1,traceback.format_exc().encode())
        raise SystemExit(1)
