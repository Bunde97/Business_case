import sys

edits = []

edits.append((
"""        inp.addEventListener('input',function(e){
          var v=parseFloat(e.target.value);
          if(isNaN(v)) v=0;
          v=Math.max(0,Math.min(100,v));
          var a=sdRampPcts[id]||[];
          a[year-1]=v;
          sdRampPcts[id]=a;
          updateSDRampNote();
          drawSDROIChart();
        });""",
"""        inp.addEventListener('input',function(e){
          var v=parseFloat(e.target.value);
          if(isNaN(v)) v=0;
          v=Math.max(0,Math.min(100,v));
          var a=sdRampPcts[id]||[];
          a[year-1]=v;
          sdRampPcts[id]=a;
          updateSDRampNote();
          sdRecalculate();
        });"""
))

edits.append((
"""          this.value=v;
          var aBlur=sdRampPcts[id]||[];
          aBlur[year-1]=v;
          sdRampPcts[id]=aBlur;
          updateSDRampNote();
          drawSDROIChart();
          buildSDRampGrid();""",
"""          this.value=v;
          var aBlur=sdRampPcts[id]||[];
          aBlur[year-1]=v;
          sdRampPcts[id]=aBlur;
          updateSDRampNote();
          sdRecalculate();
          buildSDRampGrid();"""
))

for fname in ['business-case.html', 'index.html']:
    with open(fname, 'r', encoding='utf-8') as f:
        data = f.read()
    for i, (old, new) in enumerate(edits, 1):
        cnt = data.count(old)
        if cnt != 1:
            print(f"{fname}: edit {i} count={cnt} -- ABORT")
            sys.exit(1)
        data = data.replace(old, new)
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(data)
    print(f"{fname}: all {len(edits)} edits applied OK")
