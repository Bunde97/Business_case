import sys

edits = []

# 1. sdSelectScaleStart + sdSelectScaleEnd
edits.append((
"""  function sdSelectScaleStart(y){
    sdScaleStartYear=y;
    if(sdScaleEndYear<sdScaleStartYear) sdScaleEndYear=sdScaleStartYear;
    icCloseCustomSelects();
    sdRampInitScaleSelects();
    var gridEl=document.getElementById('sd-ramp-grid');
    if(gridEl&&gridEl.classList.contains('open')) buildSDRampGrid();
    updateSDRampNote();
    drawSDROIChart();
  }

  function sdSelectScaleEnd(y){
    sdScaleEndYear=y;
    if(sdScaleStartYear>sdScaleEndYear) sdScaleStartYear=sdScaleEndYear;
    icCloseCustomSelects();
    sdRampInitScaleSelects();
    var gridEl=document.getElementById('sd-ramp-grid');
    if(gridEl&&gridEl.classList.contains('open')) buildSDRampGrid();
    updateSDRampNote();
    drawSDROIChart();
  }""",
"""  function sdSelectScaleStart(y){
    sdScaleStartYear=y;
    if(sdScaleEndYear<sdScaleStartYear) sdScaleEndYear=sdScaleStartYear;
    icCloseCustomSelects();
    sdRampInitScaleSelects();
    var gridEl=document.getElementById('sd-ramp-grid');
    if(gridEl&&gridEl.classList.contains('open')) buildSDRampGrid();
    updateSDRampNote();
    sdRecalculate();
  }

  function sdSelectScaleEnd(y){
    sdScaleEndYear=y;
    if(sdScaleStartYear>sdScaleEndYear) sdScaleStartYear=sdScaleEndYear;
    icCloseCustomSelects();
    sdRampInitScaleSelects();
    var gridEl=document.getElementById('sd-ramp-grid');
    if(gridEl&&gridEl.classList.contains('open')) buildSDRampGrid();
    updateSDRampNote();
    sdRecalculate();
  }"""
))

# 2. setSDYearRange trailing drawSDROIChart
edits.append((
"""    sdRampInitScaleSelects();
    var rampGridEl=document.getElementById('sd-ramp-grid');
    if(rampGridEl&&rampGridEl.classList.contains('open')) buildSDRampGrid();
    updateSDRampNote();
    drawSDROIChart();
  }

  // ── Benefit Ramp-Up helpers ──""",
"""    sdRampInitScaleSelects();
    var rampGridEl=document.getElementById('sd-ramp-grid');
    if(rampGridEl&&rampGridEl.classList.contains('open')) buildSDRampGrid();
    updateSDRampNote();
    sdRecalculate();
  }

  // ── Benefit Ramp-Up helpers ──"""
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
