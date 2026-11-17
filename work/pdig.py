"""Polygon diagonal intersection graph of the regular n-gon.
Vertices: polygon vertices + all interior intersection points of diagonals.
Edges: consecutive points along each side/diagonal."""
import math, itertools, sys
def build(n, eps=1e-9):
    P=[(math.cos(2*math.pi*k/n), math.sin(2*math.pi*k/n)) for k in range(n)]
    ids={}; pts=[]
    def vid(x,y):
        k=(round(x/eps/100), round(y/eps/100))
        # tolerant lookup: check neighbouring cells
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                kk=(k[0]+dx,k[1]+dy)
                if kk in ids: return ids[kk]
        ids[k]=len(pts); pts.append((x,y)); return ids[k]
    for p in P: vid(*p)
    chords=list(itertools.combinations(range(n),2))
    on={c:[] for c in chords}
    for c in chords:
        on[c]+= [(0.0,c[0]),(1.0,c[1])]
    for (a,b),(c,d) in itertools.combinations(chords,2):
        if len({a,b,c,d})<4: continue
        # chords cross iff endpoints interleave: a<c<b<d (a<b,c<d, a<c by ordering)
        if not (a<c<b<d): continue
        x1,y1=P[a];x2,y2=P[b];x3,y3=P[c];x4,y4=P[d]
        den=(x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
        t=((x1-x3)*(y3-y4)-(y1-y3)*(x3-x4))/den
        u=((x1-x3)*(y1-y2)-(y1-y3)*(x1-x2))/den
        x=x1+t*(x2-x1); y=y1+t*(y2-y1)
        v=vid(x,y)
        on[(a,b)].append((t,v)); on[(c,d)].append((u,v))
    E=set()
    for c in chords:
        l=sorted(set(on[c])); seq=[]
        for t,v in l:
            if not seq or seq[-1]!=v: seq.append(v)
        for p,q in zip(seq,seq[1:]): E.add((min(p,q),max(p,q)))
    return len(pts), sorted(E), pts
if __name__=='__main__':
    for n in range(3,21):
        N,E,_=build(n); print(n,N,len(E))
