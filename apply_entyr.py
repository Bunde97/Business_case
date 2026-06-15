import sys

edits = []

# 1. State variable
edits.append((
"""  var sdRampPcts = {sd_s1:[100], sd_s2:[100], sd_s3:[100], sd_s4:[100], sd_s5:[100]};
  var sdRampSelected = 'sd_s1';
  // Ongoing expansion: window of project-years during which new entity cohorts are created.
  var sdScaleStartYear = 1;
  var sdScaleEndYear = sdYearRange;
""",
"""  var sdRampPcts = {sd_s1:[100], sd_s2:[100], sd_s3:[100], sd_s4:[100], sd_s5:[100]};
  var sdRampSelected = 'sd_s1';
  // Ongoing expansion: window of project-years during which new entity cohorts are created.
  var sdScaleStartYear = 1;
  var sdScaleEndYear = sdYearRange;
  // Per-year override of how many new entities are added in each project-year (sparse array,
  // index 0 = year 1). Undefined entries default to sdP.entitiesPerYear. Each value is capped
  // at sdP.entitiesPerYear and only meaningful within [sdScaleStartYear, sdScaleEndYear].
  var sdEntitiesPerYearArr = [];
"""
))

# 2. HTML button+grid addition
edits.append((
"""            <div class="impl-grid-wrap" id="sd-ramp-grid"></div>
          </div>
        </div>

        <!-- Summary stats -->""",
"""            <div class="impl-grid-wrap" id="sd-ramp-grid"></div>
            <div class="sd-entyr-wrap" id="sd-entyr-wrap" style="display:none">
              <div style="display:flex;align-items:center;justify-content:flex-start;gap:8px;flex-wrap:wrap;margin-top:8px">
                <button class="impl-toggle-btn" data-i18n="btn_edit_entities_by_year" id="sd-entyr-btn" onclick="toggleSDEntYrGrid()">▸ Edit entities per year</button>
              </div>
              <div class="impl-grid-wrap" id="sd-entyr-grid"></div>
            </div>
          </div>
        </div>

        <!-- Summary stats -->"""
))

# 3. sdRampInitScaleSelects - top
edits.append((
"""  function sdRampInitScaleSelects(){
    var row = document.getElementById('sd-scale-row');
    if(!row) return;
    var relevant = (sdRampSelected==='sd_s1'||sdRampSelected==='sd_s5');
    row.style.display = (sdMarketEntryRecurring && relevant) ? 'flex' : 'none';
    if(!sdMarketEntryRecurring || !relevant) return;
    var nY = sdYearRange||5;""",
"""  function sdRampInitScaleSelects(){
    var row = document.getElementById('sd-scale-row');
    var entWrap = document.getElementById('sd-entyr-wrap');
    if(!row) return;
    var show = sdMarketEntryRecurring;
    row.style.display = show ? 'flex' : 'none';
    if(entWrap) entWrap.style.display = show ? '' : 'none';
    if(!show){
      var entGridClosed=document.getElementById('sd-entyr-grid');
      if(entGridClosed) entGridClosed.classList.remove('open');
      return;
    }
    var nY = sdYearRange||5;"""
))

# 4. sdRampInitScaleSelects - bottom
edits.append((
"""    if(startLbl) startLbl.textContent=sdScaleYearLabel(sdScaleStartYear);
    if(endLbl) endLbl.textContent=sdScaleYearLabel(sdScaleEndYear);
  }

  function sdSelectScaleStart(y){""",
"""    if(startLbl) startLbl.textContent=sdScaleYearLabel(sdScaleStartYear);
    if(endLbl) endLbl.textContent=sdScaleYearLabel(sdScaleEndYear);
    var entGridEl=document.getElementById('sd-entyr-grid');
    if(entGridEl && entGridEl.classList.contains('open')) buildSDEntYrGrid();
  }

  function sdSelectScaleStart(y){"""
))

# 5. New functions after toggleSDRampGrid
edits.append((
"""  function toggleSDRampGrid(){
    var gridEl=document.getElementById('sd-ramp-grid');
    var btn=document.getElementById('sd-ramp-btn');
    if(!gridEl||!btn) return;
    var open=gridEl.classList.toggle('open');
    btn.textContent = open ? t('btn_hide_year') : t('btn_edit_by_year');
    if(open) buildSDRampGrid();
  }
""",
"""  function toggleSDRampGrid(){
    var gridEl=document.getElementById('sd-ramp-grid');
    var btn=document.getElementById('sd-ramp-btn');
    if(!gridEl||!btn) return;
    var open=gridEl.classList.toggle('open');
    btn.textContent = open ? t('btn_hide_year') : t('btn_edit_by_year');
    if(open) buildSDRampGrid();
  }

  // ── Per-year "new entities added" override grid ──
  // Number of new entities created in project-year k (1-indexed). Defaults to
  // sdP.entitiesPerYear unless overridden in sdEntitiesPerYearArr, and is 0 outside
  // the [sdScaleStartYear, sdScaleEndYear] scaling window.
  function sdCohortSize(k){
    var startK = sdScaleStartYear||1;
    var endK = sdScaleEndYear||sdYearRange||5;
    if(k<startK || k>endK) return 0;
    var v = sdEntitiesPerYearArr[k-1];
    return (v!==undefined) ? v : (sdP.entitiesPerYear||0);
  }

  // Clamp any explicitly-entered per-year values to the current entitiesPerYear cap
  // (called when the "New entities per year" slider changes).
  function sdEntYrClamp(){
    var max = sdP.entitiesPerYear||0;
    for(var i=0;i<sdEntitiesPerYearArr.length;i++){
      if(sdEntitiesPerYearArr[i]===undefined) continue;
      if(sdEntitiesPerYearArr[i]>max) sdEntitiesPerYearArr[i]=max;
      if(sdEntitiesPerYearArr[i]<0) sdEntitiesPerYearArr[i]=0;
    }
  }

  var sdEntYrPendingFocusYear = null;

  function buildSDEntYrGrid(){
    var nY=sdYearRange||5;
    var gridEl=document.getElementById('sd-entyr-grid');
    if(!gridEl) return;
    var startK=sdScaleStartYear||1, endK=sdScaleEndYear||nY;
    var max=sdP.entitiesPerYear||0;
    var html='<div class="impl-year-grid">';
    for(var y=1;y<=nY;y++){
      var label = String(new Date().getFullYear()+y-1);
      var inWindow = (y>=startK && y<=endK);
      var val = inWindow ? sdCohortSize(y) : 0;
      var inputStyle = 'width:100%;min-width:0;flex:1 1 0%';
      if(!inWindow) inputStyle += ';color:#86868b';
      html += '<div class="impl-year-cell">'
        + '<label>' + label + '</label>'
        + '<div style="display:flex;align-items:center;gap:3px;min-width:0">'
        + '<input type="text" inputmode="numeric" id="sd-entyr-y' + y + '" value="' + val + '" data-auto="' + (inWindow?'0':'1') + '"' + (inWindow?'':' disabled') + ' style="' + inputStyle + '">'
        + '</div>'
        + '</div>';
    }
    html += '</div>';
    gridEl.innerHTML = html;
    for(var yr=1;yr<=nY;yr++){
      (function(year){
        if(year<startK || year>endK) return;
        var inp=document.getElementById('sd-entyr-y'+year);
        if(!inp) return;
        inp.addEventListener('input',function(e){
          var v=parseFloat(e.target.value);
          if(isNaN(v)) v=0;
          v=Math.max(0,Math.min(max,v));
          sdEntitiesPerYearArr[year-1]=v;
          sdRecalculate();
        });
        inp.addEventListener('keydown',function(e){
          if(e.key==='Enter'){ e.preventDefault(); e.target.blur(); }
          if(e.key==='Tab'){
            var next = e.shiftKey ? year-1 : year+1;
            if(next>=startK && next<=endK){
              e.preventDefault();
              sdEntYrPendingFocusYear = next;
              e.target.blur();
            }
          }
        });
        inp.addEventListener('focus',function(){
          this.select();
        });
        inp.addEventListener('blur',function(){
          var v=parseFloat(this.value);
          if(isNaN(v)||v<0) v=0;
          if(v>max) v=max;
          this.value=v;
          sdEntitiesPerYearArr[year-1]=v;
          sdRecalculate();
          if(sdEntYrPendingFocusYear!==null){
            var ny=sdEntYrPendingFocusYear;
            sdEntYrPendingFocusYear=null;
            var target=document.getElementById('sd-entyr-y'+ny);
            if(target){ target.focus(); target.select(); }
          }
        });
      })(yr);
    }
  }

  function toggleSDEntYrGrid(){
    var gridEl=document.getElementById('sd-entyr-grid');
    var btn=document.getElementById('sd-entyr-btn');
    if(!gridEl||!btn) return;
    var open=gridEl.classList.toggle('open');
    btn.textContent = open ? t('btn_hide_entities_by_year') : t('btn_edit_entities_by_year');
    if(open) buildSDEntYrGrid();
  }
"""
))

# 6. sdBenefitContribution
edits.append((
"""  function sdBenefitContribution(benefitId, year, base, useCohort, dropAfter100, entityScale){
    var b = base * (entityScale!==undefined ? entityScale : 1);
    if(!b) return 0;
    if(useCohort){
      var sum=0;
      var startK = sdScaleStartYear||1;
      var endK = Math.min(sdScaleEndYear||year, year);
      for(var k=startK;k<=endK;k++) sum += sdRampPctForAge(benefitId,year-k+1,dropAfter100);
      return b * (sum/100);
    }
    return b * (sdRampPctForAge(benefitId,year,dropAfter100)/100);
  }""",
"""  function sdBenefitContribution(benefitId, year, base, useCohort, dropAfter100, entityScale){
    var b = base * (entityScale!==undefined ? entityScale : 1);
    if(!b) return 0;
    if(useCohort){
      var sum=0;
      var startK = sdScaleStartYear||1;
      var endK = Math.min(sdScaleEndYear||year, year);
      var perYear = sdP.entitiesPerYear||0;
      for(var k=startK;k<=endK;k++){
        var ratio = perYear>0 ? (sdCohortSize(k)/perYear) : 0;
        sum += ratio * sdRampPctForAge(benefitId,year-k+1,dropAfter100);
      }
      return b * (sum/100);
    }
    return b * (sdRampPctForAge(benefitId,year,dropAfter100)/100);
  }"""
))

# 7. sdEffectiveEntities
edits.append((
"""  function sdEffectiveEntities(year){
    var base = sdP.entities||0;
    var perYear = sdP.entitiesPerYear||0;
    if(sdMarketEntryRecurring){
      var startK = sdScaleStartYear||1;
      var endK = sdScaleEndYear||year;
      var cohorts = (year>=startK) ? (Math.min(endK,year)-startK+1) : 0;
      if(cohorts<0) cohorts=0;
      return base + perYear*cohorts;
    }
    return base + perYear;
  }""",
"""  function sdEffectiveEntities(year){
    var base = sdP.entities||0;
    var perYear = sdP.entitiesPerYear||0;
    if(sdMarketEntryRecurring){
      var startK = sdScaleStartYear||1;
      var endK = Math.min(sdScaleEndYear||year, year);
      var added = 0;
      if(year>=startK) for(var k=startK;k<=endK;k++) added += sdCohortSize(k);
      return base + added;
    }
    return base + perYear;
  }"""
))

# 8. slider oninput
edits.append((
"""      sl.oninput=function(){
        var v=parseFloat(this.value)||0;
        sdP[s.key]=v;
        dp.textContent=s.fmt(v);
        sdRecalculate();
      };""",
"""      sl.oninput=function(){
        var v=parseFloat(this.value)||0;
        sdP[s.key]=v;
        dp.textContent=s.fmt(v);
        if(s.key==='entitiesPerYear'){
          sdEntYrClamp();
          var entGridEl=document.getElementById('sd-entyr-grid');
          if(entGridEl&&entGridEl.classList.contains('open')) buildSDEntYrGrid();
        }
        sdRecalculate();
      };"""
))

# 9. exportSettings
edits.append((
"""        marketEntryRecurring: sdMarketEntryRecurring,
        rampPcts: JSON.parse(JSON.stringify(sdRampPcts)),
        scaleStartYear: sdScaleStartYear,
        scaleEndYear: sdScaleEndYear
      }""",
"""        marketEntryRecurring: sdMarketEntryRecurring,
        rampPcts: JSON.parse(JSON.stringify(sdRampPcts)),
        scaleStartYear: sdScaleStartYear,
        scaleEndYear: sdScaleEndYear,
        entitiesPerYearArr: JSON.parse(JSON.stringify(sdEntitiesPerYearArr))
      }"""
))

# 10. applyImport
edits.append((
"""      if(data.sd.marketEntryRecurring!==undefined) sdMarketEntryRecurring=data.sd.marketEntryRecurring;
      if(data.sd.rampPcts) sdRampPcts=data.sd.rampPcts;
      if(data.sd.scaleStartYear!==undefined) sdScaleStartYear=data.sd.scaleStartYear;
      if(data.sd.scaleEndYear!==undefined) sdScaleEndYear=data.sd.scaleEndYear;
      if(currentArea==='sd') sdInit();""",
"""      if(data.sd.marketEntryRecurring!==undefined) sdMarketEntryRecurring=data.sd.marketEntryRecurring;
      if(data.sd.rampPcts) sdRampPcts=data.sd.rampPcts;
      if(data.sd.scaleStartYear!==undefined) sdScaleStartYear=data.sd.scaleStartYear;
      if(data.sd.scaleEndYear!==undefined) sdScaleEndYear=data.sd.scaleEndYear;
      if(data.sd.entitiesPerYearArr) sdEntitiesPerYearArr=data.sd.entitiesPerYearArr;
      if(currentArea==='sd') sdInit();"""
))

# 11. i18n EN
edits.append((
"sd_scale_label:'New entities added',sd_scale_to:'to'",
"sd_scale_label:'New entities added',sd_scale_to:'to',btn_edit_entities_by_year:'▸ Edit entities per year',btn_hide_entities_by_year:'▾ Hide entities breakdown'"
))

# 12. i18n DA
edits.append((
"sd_scale_label:'Nye selskaber tilføjes',sd_scale_to:'til'",
"sd_scale_label:'Nye selskaber tilføjes',sd_scale_to:'til',btn_edit_entities_by_year:'▸ Rediger antal pr. år',btn_hide_entities_by_year:'▾ Skjul antalsfordeling'"
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
