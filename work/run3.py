"""Driver: choose conditioning set C to cap memory, run pathdp2 in parallel, combine."""
import sys, math, subprocess, json, time
from concurrent.futures import ThreadPoolExecutor
from pdig import build
def lifetimes(N,adj,order,C):
    """slot usage mirroring pathdp2.c; returns (peak, list of active sets per step)"""
    done=[0]*N; act=set(); sets=[]
    for u in order:
        for v in adj[u]:
            done[v]+=1
            if v not in C and done[v]<=len(adj[v]) and v not in act and done[v]==1: act.add(v)
        sets.append(frozenset(act))
        for v in adj[u]+[u]:
            if v in act and done[v]==len(adj[v]): act.discard(v)
    return max(len(s) for s in sets), sets
def choose_C(N,adj,order,target):
    C=[]
    while True:
        peak,sets=lifetimes(N,adj,order,set(C))
        if peak<=target: return C,peak,sets
        # vertex present in the most steps that are within 1 of the peak; tie -> longest lifetime
        cnt={}; life={}
        for s in sets:
            for v in s: life[v]=life.get(v,0)+1
            if len(s)>=peak:
                for v in s: cnt[v]=cnt.get(v,0)+1
        C.append(max(cnt,key=lambda v:(cnt[v],life[v])))
def count(n,order,target,nw=3,procs=14,chunks_per=4,rawgraph=None):
    if rawgraph: N,E=rawgraph
    else: N,E,_=build(n)
    adj=[[] for _ in range(N)]
    for a,b in E: adj[a].append(b);adj[b].append(a)
    C,peak,sets=choose_C(N,adj,order,target)
    work=math.log2(sum(2.0**len(s) for s in sets))+len(C)
    print('n=%s N=%d |C|=%d peak=%d est work=2^%.1f'%(n,N,len(C),peak,work),file=sys.stderr,flush=True)
    inp="%d %d %d %d\n"%(N,len(E),max(peak,1),len(C))+"\n".join("%d %d"%e for e in E)+"\n"+" ".join(map(str,order))+"\n"+" ".join(map(str,C))+"\n"
    tot=1<<len(C); nch=min(tot,procs*chunks_per); mod=1<<(64*nw)
    bounds=[tot*i//nch for i in range(nch+1)]
    def job(i):
        r=subprocess.run(['./pathdp3_%d'%nw,str(bounds[i]),str(bounds[i+1])],input=inp,capture_output=True,text=True)
        if r.returncode: raise RuntimeError(r.stderr)
        return int(r.stdout.strip(),16)
    t=time.time(); s=0
    with ThreadPoolExecutor(procs) as ex:
        for k,r in enumerate(ex.map(job,range(nch))):
            s=(s+r)%mod
    assert s < (1<<N), "result exceeds 2^N: wraparound or bug"
    print('elapsed %.1fs'%(time.time()-t),file=sys.stderr,flush=True)
    return s
if __name__=='__main__':
    n=int(sys.argv[1]); target=int(sys.argv[2]); src=sys.argv[3]
    order=json.load(open(src))['order']
    nw=3 if n<=10 else 6
    print(n,count(n,order,target,nw))
