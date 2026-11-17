"""Resumable long run.  usage: launch2.py kind n target procs tag chunk_bits   (kind = tds | dom)"""
import sys, json, math, os, subprocess, time
from concurrent.futures import ThreadPoolExecutor
from pdig import build
from condplan import plan, candidates
kind,n,target,procs,tag,cb=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),sys.argv[5],int(sys.argv[6])
pf='plan_%s.json'%tag
if os.path.exists(pf): pl=json.load(open(pf))
else:
    N,E,pts=build(n)
    if kind=='dom': E=E+[(v,v) for v in range(N)]
    adj=[[] for _ in range(N)]
    for a,b in E:
        adj[a].append(b)
        if a!=b: adj[b].append(a)
    best=None
    for name,o in candidates(N,pts,120):
        C,w,pk=plan(N,adj,o,target)
        if best is None or w<best[0]: best=(w,name,C,pk,o)
    w,name,C,pk,o=best
    pl=dict(kind=kind,n=n,N=N,E=E,order=o,C=C,peak=pk,work=w,name=name); json.dump(pl,open(pf,'w'))
N,E,o,C,pk=pl['N'],pl['E'],pl['order'],pl['C'],pl['peak']
nw=3 if N<=190 else 6
inp="%d %d %d %d\n"%(N,len(E),max(pk,1),len(C))+"\n".join("%d %d"%tuple(e) for e in E)+"\n"+" ".join(map(str,o))+"\n"+" ".join(map(str,C))+"\n"
tot=1<<len(C); nch=min(tot,1<<cb); bounds=[tot*i//nch for i in range(nch+1)]
resf='res_%s.jsonl'%tag; done={}
if os.path.exists(resf):
    for l in open(resf):
        try: d=json.loads(l)
        except ValueError: continue      # torn last line after a crash
        done[(d['lo'],d['hi'])]=int(d['val'],16)
todo=[i for i in range(nch) if (bounds[i],bounds[i+1]) not in done]
print('%s: %s N=%d |C|=%d peak=%d est work 2^%.2f chunks %d (todo %d)'%(tag,kind,N,len(C),pk,pl['work'],nch,len(todo)),flush=True)
def job(i):
    r=subprocess.run(['./pathdp4_%d'%nw,str(bounds[i]),str(bounds[i+1])],input=inp,capture_output=True,text=True)
    if r.returncode: raise RuntimeError(r.stderr)
    return i,r.stdout.strip()
t0=time.time()
with ThreadPoolExecutor(procs) as ex, open(resf,'a') as f:
    for k,(i,val) in enumerate(ex.map(job,todo)):
        f.write(json.dumps(dict(lo=bounds[i],hi=bounds[i+1],val=val))+"\n"); f.flush()
        done[(bounds[i],bounds[i+1])]=int(val,16)
        if (k+1)%max(1,len(todo)//50)==0:
            el=time.time()-t0; print('  %d/%d chunks, %.0fs elapsed, eta %.0fs'%(k+1,len(todo),el,el*(len(todo)-k-1)/(k+1)),flush=True)
assert sorted(done)==[(bounds[i],bounds[i+1]) for i in range(nch)], 'chunk set mismatch'
s=sum(done.values())%(1<<(64*nw)); assert s<(1<<N), 'result exceeds 2^N'
print(kind,n,s,flush=True); open('result_%s.txt'%tag,'w').write('%s %d %d\n'%(kind,n,s))
