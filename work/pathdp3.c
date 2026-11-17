// Total dominating sets, vertex-ordering DP with inclusion-exclusion conditioning.
// For a set C of "conditioned" vertices:  #TDS = sum_{T subset C} (-1)^|T| * #{S : every v not in C
// has a nbr in S, and no vertex of N(T) is in S}.  C-vertices then need no state bit.
// Input (stdin): N M W K ; M edges ; order (N ints) ; C (K ints).  Args: lo hi (range of T masks).
// Output: signed sum over T in [lo,hi), as hex mod 2^(64*NW).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#ifndef NW
#define NW 3
#endif
typedef struct { uint64_t w[NW]; } big;
static inline void addto(big*a,const big*b){ unsigned __int128 c=0; for(int i=0;i<NW;i++){ c+=(unsigned __int128)a->w[i]+b->w[i]; a->w[i]=(uint64_t)c; c>>=64;} }
static inline void subfrom(big*a,const big*b){ unsigned __int128 br=0; for(int i=0;i<NW;i++){ unsigned __int128 d=(unsigned __int128)a->w[i]-b->w[i]-br; a->w[i]=(uint64_t)d; br=(d>>64)&1;} }
int N,M,W,K; int *deg,**adj,*order,*Cv; big *A,*X;
static big run(uint64_t T){
  char *exempt=calloc(N,1),*forced=calloc(N,1);
  for(int i=0;i<K;i++){ exempt[Cv[i]]=1; if(T>>i&1) for(int j=0;j<deg[Cv[i]];j++) forced[adj[Cv[i]][j]]=1; }
  int *slot=malloc(N*sizeof(int)); for(int i=0;i<N;i++) slot[i]=-1;
  int *done=calloc(N,sizeof(int)); uint64_t freem=((uint64_t)1<<W)-1, used=0;
  A[0].w[0]=1;   // invariant: A is zero outside submasks of 'used'
  for(int step=0;step<N;step++){
    int u=order[step]; uint64_t Mk=0;
    uint64_t Mo=0,Mn=0; uint64_t Uold=used;
    for(int j=0;j<deg[u];j++){ int v=adj[u][j]; done[v]++; if(exempt[v]) continue;
      if(slot[v]<0){ if(!freem){fprintf(stderr,"out of slots at step %d\n",step);exit(3);}
        int s=__builtin_ctzll(freem); freem&=freem-1; slot[v]=s; used|=1ULL<<s; Mn|=1ULL<<s; }
      else Mo|=1ULL<<slot[v]; }
    // invariant: A is zero outside submasks of Uold.  u not in S: A unchanged.
    // u in S: every state t (submask of Uold) moves to t|Mo|Mn.
    if(!forced[u]){
      uint64_t R=Uold&~Mo, t=0;
      do{ big sum=A[t]; uint64_t s=Mo; while(s){ addto(&sum,&A[t|s]); s=(s-1)&Mo; }
          if(Mn) A[t|Mo|Mn]=sum; else addto(&A[t|Mo],&sum);
          t=(t-R)&R; }while(t);
    }
    uint64_t U=used;
    for(int j=0;j<=deg[u];j++){ int v=(j<deg[u])?adj[u][j]:u;
      if(slot[v]>=0 && done[v]==deg[v]){ uint64_t b=1ULL<<slot[v]; uint64_t R=U&~b; uint64_t t=0;
        do{ A[t]=A[t|b]; memset(&A[t|b],0,sizeof(big)); t=(t-R)&R; }while(t);
        used&=~b; U=used; freem|=b; slot[v]=-2; } }
  }
  if(used){fprintf(stderr,"leftover slots\n");exit(4);}
  big r=A[0]; memset(&A[0],0,sizeof(big)); free(exempt);free(forced);free(slot);free(done); return r;
}
int main(int argc,char**argv){
  if(scanf("%d %d %d %d",&N,&M,&W,&K)!=4) return 1;
  int *ea=malloc(M*sizeof(int)),*eb=malloc(M*sizeof(int)); deg=calloc(N,sizeof(int)); adj=malloc(N*sizeof(int*));
  for(int i=0;i<M;i++){scanf("%d %d",&ea[i],&eb[i]);deg[ea[i]]++;deg[eb[i]]++;}
  int *fill=calloc(N,sizeof(int)); for(int i=0;i<N;i++) adj[i]=malloc(deg[i]*sizeof(int));
  for(int i=0;i<M;i++){adj[ea[i]][fill[ea[i]]++]=eb[i];adj[eb[i]][fill[eb[i]]++]=ea[i];}
  order=malloc(N*sizeof(int)); for(int i=0;i<N;i++) scanf("%d",&order[i]);
  Cv=malloc((K+1)*sizeof(int)); for(int i=0;i<K;i++) scanf("%d",&Cv[i]);
  uint64_t lo=strtoull(argv[1],0,10),hi=strtoull(argv[2],0,10);
  size_t S=(size_t)1<<W; A=calloc(S,sizeof(big));
  if(!A){fprintf(stderr,"alloc\n");return 1;}
  big tot; memset(&tot,0,sizeof tot);
  for(uint64_t T=lo;T<hi;T++){ big r=run(T); if(__builtin_popcountll(T)&1) subfrom(&tot,&r); else addto(&tot,&r); }
  printf("0x"); for(int i=NW-1;i>=0;i--) printf("%016llx",(unsigned long long)tot.w[i]); printf("\n");
  return 0;
}
