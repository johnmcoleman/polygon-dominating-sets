// Independent method: #TDS = sum over (S,T) of (-1)^|T| prod_{edges uv} [not(t_u&s_v)][not(t_v&s_u)]
// (inclusion-exclusion over the set T of vertices left undominated).  This is a pairwise 4-state
// model on G, evaluated by variable elimination, modulo a compile-time prime P.
// Input: N M ; edges ; elimination order.  Output: result mod P.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#ifndef P
#define P 4611686018427387847ULL
#endif
typedef unsigned __int128 u128;
static inline uint64_t mulm(uint64_t a,uint64_t b){ return (uint64_t)((u128)a*b%P); }
typedef struct { int k; int *sc; uint64_t *t; int alive; } fac;  // scope sorted by elimination position, sc[0] earliest
int N,M; int *pos;
int main(){
  scanf("%d %d",&N,&M); int *ea=malloc(M*4),*eb=malloc(M*4);
  for(int i=0;i<M;i++) scanf("%d %d",&ea[i],&eb[i]);
  int *order=malloc(N*4); pos=malloc(N*4); for(int i=0;i<N;i++){scanf("%d",&order[i]);pos[order[i]]=i;}
  int cap=M+N+5,nf=0; fac *F=malloc(cap*sizeof(fac));
  for(int i=0;i<M;i++){ int a=ea[i],b=eb[i]; if(pos[a]>pos[b]){int t=a;a=b;b=t;}
    fac f; f.alive=1;
    if(a==b){ f.k=1; f.sc=malloc(4); f.sc[0]=a; f.t=malloc(4*8); for(int x=0;x<4;x++) f.t[x]=(x!=3); F[nf++]=f; continue; } // loop: v dominates itself
    f.k=2; f.sc=malloc(8); f.sc[0]=a; f.sc[1]=b; f.t=malloc(16*8);
    for(int x=0;x<4;x++) for(int y=0;y<4;y++){ int sx=x&1,tx=x>>1,sy=y&1,ty=y>>1; f.t[x|(y<<2)]=!(tx&&sy)&&!(ty&&sx); }
    F[nf++]=f; }
  uint64_t scalar=1; int maxk=0;
  for(int step=0;step<N;step++){
    int v=order[step];
    int idx[64],ni=0; for(int i=0;i<nf;i++) if(F[i].alive && F[i].sc[0]==v) idx[ni++]=i;
    // union scope minus v, sorted by pos
    char *in=calloc(N,1); int *sc=malloc(N*4); int k=0;
    for(int a=0;a<ni;a++) for(int j=1;j<F[idx[a]].k;j++){ int w=F[idx[a]].sc[j]; if(!in[w]){in[w]=1;sc[k++]=w;} }
    for(int i=1;i<k;i++){ int w=sc[i],j=i; while(j>0&&pos[sc[j-1]]>pos[w]){sc[j]=sc[j-1];j--;} sc[j]=w; }
    if(k>maxk) maxk=k;
    if(k>16){fprintf(stderr,"scope too large %d\n",k);return 2;}
    // for each factor: lookup tables mapping output index (2k bits) -> factor index (excluding v digit)
    // split output index into low 16 bits and high bits
    uint32_t *lo[64],*hi[64]; int hb=(2*k>16)?2*k-16:0, lb=2*k-hb;
    for(int a=0;a<ni;a++){ fac*f=&F[idx[a]]; int dpos[32]; // digit position in factor for each output digit, or -1
      for(int d=0;d<k;d++){ dpos[d]=-1; for(int j=1;j<f->k;j++) if(f->sc[j]==sc[d]) dpos[d]=j; }
      lo[a]=malloc(((size_t)1<<lb)*4); hi[a]=malloc(((size_t)1<<hb)*4);
      for(uint32_t x=0;x<(1u<<lb);x++){ uint32_t r=0; for(int d=0;d<lb/2;d++) if(dpos[d]>=0) r|=((x>>(2*d))&3u)<<(2*dpos[d]); lo[a][x]=r; }
      for(uint32_t x=0;x<(1u<<hb);x++){ uint32_t r=0; for(int d=0;d<hb/2;d++) if(dpos[d+lb/2]>=0) r|=((x>>(2*d))&3u)<<(2*dpos[d+lb/2]); hi[a][x]=r; }
    }
    size_t S=(size_t)1<<(2*k); uint64_t *out=malloc(S*8); if(!out){fprintf(stderr,"alloc\n");return 1;}
    uint32_t lm=(1u<<lb)-1;
    for(size_t i=0;i<S;i++){
      uint64_t acc=0;
      for(int x=0;x<4;x++){ uint64_t pr=1;
        for(int a=0;a<ni;a++){ uint32_t fi=lo[a][i&lm]|hi[a][i>>lb]; uint64_t e=F[idx[a]].t[fi|x]; 
          if(e==0){pr=0;break;} if(e!=1) pr=mulm(pr,e); }
        if(x>>1) { acc+= pr?P-pr:0; } else acc+=pr;   // weight (-1)^{t_v}
        if(acc>=P) acc-=P; }
      out[i]=acc;
    }
    for(int a=0;a<ni;a++){ free(lo[a]);free(hi[a]); free(F[idx[a]].t); free(F[idx[a]].sc); F[idx[a]].alive=0; }
    free(in);
    if(k==0){ scalar=mulm(scalar,out[0]); free(out); free(sc); }
    else { fac f; f.k=k+1; f.sc=malloc((k+1)*4); f.sc[0]=sc[0];
      // new factor's "digit 0" must be its earliest variable sc[0]; store with a dummy layout:
      // we keep scope (sc[0],sc[1..]) and table index = digits in that order, which is exactly out's index
      // but factor convention reserves the low 2 bits for sc[0]: out index digit 0 is sc[0] already.
      for(int j=0;j<k;j++) f.sc[j]=sc[j]; f.k=k; f.t=out; f.alive=1; free(sc);
      if(nf==cap){cap*=2;F=realloc(F,cap*sizeof(fac));} F[nf++]=f; }
  }
  fprintf(stderr,"max scope %d\n",maxk);
  printf("%llu\n",(unsigned long long)scalar); return 0;
}
