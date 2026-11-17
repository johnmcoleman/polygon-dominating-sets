"""Driver v4: angular/sweep order + conditioning set from condplan; resumable chunked parallel run of pathdp3."""
import sys, math, subprocess, json, time, os
from concurrent.futures import ThreadPoolExecutor
from pdig import build
from condplan import plan, candidates
def make_plan(n,target,k=120,order=None):
    N,E,pts=build(n)
    adj=[[] for _ in range(N)]
    for a,b in E: adj[a].append(b);adj[b].append(a)
    best=None
    cands=[(('given',0),order)] if order else candidates(N,pts,k)
    for name,o in cands:
        C,w,pk=plan(N,adj,o,target)
        if best is None or w<best[0]: best=(w,name,C,pk,o)
    w,name,C,pk,o=best
    return dict(n=n,N=N,E=E,order=o,C=C,peak=pk,work=w,name=name)
def run(pl,nw,procs,tag,chunk_bits=None):
    N,E,o,C,pk=pl['N'],pl['E'],pl['order'],pl['C'],pl['peak']
    inp="%d %d %d %d\n"%(N,len(E),max(pk,1),len(C))+"\n".join("%d %d"%tuple(e) for e in E)+"\n"+" ".join(map(str,o))+"\n"+" ".join(map(str,C))+"\n"
    tot=1<<len(C)
    nch=min(tot, 1<<chunk_bits if chunk_bits is not None else procs*8)
    bounds=[tot*i//nch for i in range(nch+1)]
    resf='res_%s.jsonl'%tag; done={}
    if os.path.exists(resf):
        for l in open(resf):
            d=json.loads(l); done[(d['lo'],d['hi'])]=int(d['val'],16)
    mod=1<<(64*nw); t0=time.time()
    todo=[i for i in range(nch) if (bounds[i],bounds[i+1]) not in done]
    print('%s: N=%d |C|=%d peak=%d est work 2^%.2f chunks %d (todo %d)'%(tag,N,len(C),pk,pl['work'],nch,len(todo)),file=sys.stderr,flush=True)
    def job(i):
        r=subprocess.run(['./pathdp3_%d'%nw,str(bounds[i]),str(bounds[i+1])],input=inp,capture_output=True,text=True)
        if r.returncode: raise RuntimeError(r.stderr)
        return i,r.stdout.strip()
    with ThreadPoolExecutor(procs) as ex, open(resf,'a') as f:
        for k,(i,val) in enumerate(ex.map(job,todo)):
            f.write(json.dumps(dict(lo=bounds[i],hi=bounds[i+1],val=val))+"\n"); f.flush()
            done[(bounds[i],bounds[i+1])]=int(val,16)
            if (k+1)%max(1,len(todo)//50)==0:
                el=time.time()-t0; print('  %d/%d chunks, %.0fs elapsed, eta %.0fs'%(k+1,len(todo),el,el*(len(todo)-k-1)/(k+1)),file=sys.stderr,flush=True)
    assert sorted(done)==[(bounds[i],bounds[i+1]) for i in range(nch)], 'chunk set mismatch (plan changed?)'
    s=sum(done.values())%mod
    assert s < (1<<N), 'result exceeds 2^N'
    print('elapsed %.1fs'%(time.time()-t0),file=sys.stderr,flush=True)
    return s
if __name__=='__main__':
    n=int(sys.argv[1]); target=int(sys.argv[2]); procs=int(sys.argv[3]); tag=sys.argv[4]
    pf='plan_%s.json'%tag
    if os.path.exists(pf): pl=json.load(open(pf))
    else:
        pl=make_plan(n,target); json.dump(pl,open(pf,'w'))
    nw=3 if pl['N']<=190 else 6
    print(n,run(pl,nw,procs,tag))
