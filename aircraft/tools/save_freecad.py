"""Run with a Python interpreter that can import FreeCAD's modules.
Imports the named STEP assembly into an editable FreeCAD document.
The model is parametrically regenerated in build_cad.py, not a native sketch tree.
"""
from pathlib import Path
import sys,json
for p in ['/usr/lib/freecad-python3/lib','/usr/lib/freecad/lib']:
    if Path(p).exists():sys.path.append(p)
import FreeCAD as App
import Import
ROOT=Path(__file__).resolve().parents[1]
doc=App.newDocument('E8_Concept_Assembly')
Import.insert(str(ROOT/'cad'/'E8_Winged_Hover.step'),doc.Name)
doc.recompute()
checks=[]
for obj in doc.Objects:
    if hasattr(obj,'Shape') and not obj.Shape.isNull():
        checks.append(dict(name=obj.Name,label=obj.Label,valid=obj.Shape.isValid(),solids=len(obj.Shape.Solids)))
doc.saveAs(str(ROOT/'cad'/'E8_Concept_Assembly.FCStd'))
(ROOT/'cad'/'freecad_import_checks.json').write_text(json.dumps(dict(version=App.Version(),objects=checks),indent=2)+'\n')
print('FreeCAD document saved:',len(checks),'shape-bearing objects')
