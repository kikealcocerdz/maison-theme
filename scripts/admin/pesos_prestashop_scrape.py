import json,re,time,urllib.request,urllib.parse,sys
UA={'User-Agent':'Mozilla/5.0'}
def get(u):
    for i in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode('utf-8','replace')
        except Exception as e: err=e; time.sleep(3)
    raise err
rows=json.load(open('variants.json'))
skus=sorted({r['sku'].strip() for r in rows if r['sku']})
out={}
try: out=json.load(open('pesos.json'))
except: pass
for i,s in enumerate(skus):
    if s in out: continue
    try:
        h=get('https://lacartujadesevilla.com/buscar?controller=search&s='+urllib.parse.quote(s))
        urls=list(dict.fromkeys(re.findall(r'https://lacartujadesevilla\.com/[a-z0-9-]+/\d+-[^"#?]+\.html',h)))
        hit=None
        for u in urls[:4]:
            p=get(u); time.sleep(0.4)
            sk=re.search(r'"sku"\s*:\s*"([^"]+)"',p); w=re.search(r'product:weight:value" content="([\d.]+)"',p)
            if sk and sk.group(1).lower()==s.lower():
                hit={'url':u,'kg':float(w.group(1)) if w else None}; break
        out[s]=hit or {'url':None,'kg':None,'cand':urls[:4]}
    except Exception as e: out[s]={'err':str(e)}
    if i%20==0: json.dump(out,open('pesos.json','w'),indent=1); print(i,len(skus),s,out[s],flush=True)
    time.sleep(0.4)
json.dump(out,open('pesos.json','w'),indent=1); print('FIN')
