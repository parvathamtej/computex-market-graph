import json, os, datetime
tpl = open("build/app_template.html").read()
data = open("data/computex_dataset.json").read()
# JSON lives in a <script type="application/json"> block; only "</" needs escaping
lf = open("vendor/leaflet.js").read() + "\n;\n" + open("vendor/mc.js").read()
out = tpl.replace("__LEAFLET__", lf.replace("</script", "<\\/script"))
out = out.replace("__DATA__", data.replace("</", "<\\/"))
open("ComputeX_Market_Graph.html","w").write(out)
kb = os.path.getsize("ComputeX_Market_Graph.html")/1024
print(f"built ComputeX_Market_Graph.html  {kb:,.0f} KB")
