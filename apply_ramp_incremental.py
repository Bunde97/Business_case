import sys

edits = []

edits.append((
"""  // Effective % (0-100) at ramp-age `age` (1-indexed), based on the cumulative sum of
  // incremental per-year percentages, capped at 100%. Once the cumulative sum hits 100%,
  // either it stays at 100% forever (dropAfter100=false) or drops to 0% afterward (dropAfter100=true).
  function sdRampPctForAge(benefitId, age, dropAfter100){
    var arr = (sdRampPcts[benefitId] && sdRampPcts[benefitId].length) ? sdRampPcts[benefitId] : [100];
    var cum=0, reached=null;
    for(var a=1;a<=age;a++){
      cum += (arr[a-1]!==undefined ? arr[a-1] : 0);
      if(cum>=100 && reached===null) reached=a;
    }
    if(reached!==null) return (dropAfter100 && age>reached) ? 0 : 100;
    return Math.max(0, Math.min(cum,100));
  }""",
"""  // Effective % (0-100) at ramp-age `age` (1-indexed).
  // dropAfter100=false (recurring, e.g. Cost avoidance): cumulative sum of incremental
  // per-year percentages, capped at 100%, and stays at 100% forever once reached.
  // dropAfter100=true (one-time, e.g. Market entry speed): each age contributes only its
  // OWN incremental slice (not the running cumulative total), capped so the total realized
  // over the entity's life never exceeds 100%.
  function sdRampPctForAge(benefitId, age, dropAfter100){
    var arr = (sdRampPcts[benefitId] && sdRampPcts[benefitId].length) ? sdRampPcts[benefitId] : [100];
    if(dropAfter100){
      var cumBefore=0;
      for(var a=1;a<age;a++) cumBefore += (arr[a-1]!==undefined ? arr[a-1] : 0);
      cumBefore = Math.min(cumBefore,100);
      var remaining = Math.max(0,100-cumBefore);
      var inc = (arr[age-1]!==undefined ? arr[age-1] : 0);
      return Math.max(0, Math.min(inc, remaining));
    }
    var cum=0, reached=null;
    for(var a=1;a<=age;a++){
      cum += (arr[a-1]!==undefined ? arr[a-1] : 0);
      if(cum>=100 && reached===null) reached=a;
    }
    if(reached!==null) return 100;
    return Math.max(0, Math.min(cum,100));
  }"""
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
