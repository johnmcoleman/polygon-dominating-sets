// Count total dominating sets by a vertex-ordering DP. Exact multiword integers (additions only).
// Input: N M W ; M edges ; order of N vertices.  State: one "dominated" bit per active vertex
// (vertex with >=1 processed and >=1 unprocessed neighbour), in a stable slot.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#ifndef NW
#define NW 3
#endif
typedef struct { uint64_t w[NW]; } big;
static inline void addto(big*a,const big*b){ unsigned __int128 c=0; for(int i=0;i<NW;i++){ c+=(unsigned __int128)a->w[i]+b->w[i]; a->w[i]=(uint64_t)c; c>>=64;} if(c){fprintf(stderr,"OVERFLOW\n");exit(2);} }
int main(int argc,char**argv){
  int N,M,W; if(scanf("%d %d %d",&N,&M,&W)!=3) return 1;
  int *ea=malloc(M*sizeof(int)),*eb=malloc(M*sizeof(int));
  int *deg=calloc(N,sizeof(int)); int **adj=malloc(N*sizeof(int*));
  for(int i=0;i<M;i++){scanf("%d %d",&ea[i],&eb[i]);deg[ea[i]]++;deg[eb[i]]++;}
  int *fill=calloc(N,sizeof(int)); for(int i=0;i<N;i++) adj[i]=malloc(deg[i]*sizeof(int));
  for(int i=0;i<M;i++){adj[ea[i]][fill[ea[i]]++]=eb[i];adj[eb[i]][fill[eb[i]]++]=ea[i];}
  int *order=malloc(N*sizeof(int)); for(int i=0;i<N;i++) scanf("%d",&order[i]);
  size_t S=(size_t)1<<W;
  big *A=calloc(S,sizeof(big)),*X=malloc(S*sizeof(big));
  if(!A||!X){fprintf(stderr,"alloc\n");return 1;}
  int *slot=malloc(N*sizeof(int)); for(int i=0;i<N;i++) slot[i]=-1;
  int *done=calloc(N,sizeof(int)); uint64_t freem=S-1; uint64_t used=0;
  A[0].w[0]=1;
  for(int step=0;step<N;step++){
    int u=order[step]; uint64_t Mk=0;
    for(int j=0;j<deg[u];j++){ int v=adj[u][j];
      if(slot[v]<0){ if(!freem){fprintf(stderr,"out of slots at step %d\n",step);return 3;}
        int s=__builtin_ctzll(freem); freem&=freem-1; slot[v]=s; used|=1ULL<<s; }
      Mk|=1ULL<<slot[v]; done[v]++; }
    // X = partial zeta over bits of Mk, restricted to submasks of 'used'
    // iterate over submasks of used only
    uint64_t U=used;
    // copy A->X on submasks of U
    uint64_t s=0; do{ X[s]=A[s]; s=(s-U)&U; }while(s);
    for(uint64_t mm=Mk;mm;mm&=mm-1){ uint64_t b=mm&-mm; uint64_t R=U&~b; uint64_t t=0;
      do{ addto(&X[t|b],&X[t]); t=(t-R)&R; }while(t); }
    { uint64_t R=U&~Mk; uint64_t t=0; do{ addto(&A[t|Mk],&X[t|Mk]); t=(t-R)&R; }while(t); }
    // finalize neighbours (and u) whose neighbours are all processed
    for(int j=0;j<=deg[u];j++){ int v=(j<deg[u])?adj[u][j]:u;
      if(slot[v]>=0 && done[v]==deg[v]){ uint64_t b=1ULL<<slot[v]; uint64_t R=U&~b; uint64_t t=0;
        do{ A[t]=A[t|b]; memset(&A[t|b],0,sizeof(big)); t=(t-R)&R; }while(t);
        used&=~b; U=used; freem|=b; slot[v]=-2; } }
  }
  if(used){fprintf(stderr,"leftover slots\n");return 4;}
  // print A[0] as hex
  printf("0x"); for(int i=NW-1;i>=0;i--) printf("%016llx",(unsigned long long)A[0].w[i]); printf("\n");
  return 0;
}
