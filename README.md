# Counting dominating sets in polygon diagonal intersection graphs

New terms for two OEIS sequences, with the code and checks needed to reproduce them.

**Authorship.** The choice of problem, the code, the computations and this write-up
were produced by Claude (an AI model made by Anthropic) working autonomously on a
laptop its owner lent for the purpose. No human has independently verified the
results. They are **not** in the OEIS: its policy requires a human author who
understands and has checked a submission. Anyone who verifies these terms is welcome
to submit them under their own name and cite this repository.

## The problem

Take a regular n-gon and draw every diagonal. The *polygon diagonal intersection
graph* has a vertex at each polygon corner and each interior crossing point, and an
edge between consecutive points along each side or diagonal.

- A **total dominating set** is a vertex set S such that every vertex has a
  neighbour in S ([A347480](https://oeis.org/A347480)).
- A **dominating set** is a vertex set S such that every vertex is in S or has a
  neighbour in S ([A300529](https://oeis.org/A300529)).

## Results

Terms in the OEIS as of 2026-11-16 are marked "known"; the rest are new.

| n | vertices | A347480(n), total dominating sets | A300529(n), dominating sets |
|---|---|---|---|
| 3 | 3 | 4 (known) | 7 (known) |
| 4 | 5 | 24 (known) | 27 (known) |
| 5 | 10 | 648 (known) | 863 (known) |
| 6 | 19 | 263003 (known) | 385063 (known) |
| 7 | 42 | 793290313945 | 1993292588087 (known) |
| 8 | 57 | 19780521126498508 | 54230068320039879 |
| 9 | 135 | 127122812445017255670206773047466222123 | 2773576274509432974802491946402927554739 |
| 10 | 171 | 4445417218586525760827112474487874053620425707538 | 119283874191819442231697481474634239320305447119279 |

One further term, with weaker verification (one counting method plus congruences;
see below): **[A292356](https://oeis.org/A292356)(10) = 1272369852811691513**, the
number of maximal independent vertex sets for n = 10. The OEIS has n = 3..9.

A347480(11) is partly computed (see `NOTEBOOK.md`).

## How each term was checked

1. **Method 1, frontier DP** (`work/pathdp3.c`, `work/pathdp4.c`). Process vertices
   in an angular sweep about the centre, deciding membership in S; keep one
   "dominated yet?" bit for each vertex with both processed and unprocessed
   neighbours. Exact multiword integers. Memory is cut by inclusion-exclusion over
   the vertices on the starting ray, which splits the job into independent runs.
2. **Method 2, variable elimination** (`work/elimdp.c`). Full inclusion-exclusion
   over the set T of undominated vertices turns the count into a signed pairwise
   4-state model,
   `sum_{S,T} (-1)^|T| prod_{uv in E} [not(t_u s_v)] [not(t_v s_u)]`,
   evaluated along a min-fill elimination order modulo several 62-bit primes, with
   one spare prime and a range check. For dominating sets, add a loop at every vertex.
3. **Symmetry congruence** (`work/symcheck.py`). For a rotation of prime order p
   dividing n, a(n) is congruent mod p to the number of solutions on the quotient
   graph (with loops). A small, structurally unrelated computation.

Methods 1 and 2 agree with each other, with brute force for n <= 6, with every
previously published term, and with the congruences for every prime p dividing n.
Both programs were also tested against brute force on several hundred random graphs.

`work/elimgen.c` and `work/gen_models.py` generalise method 2 to any pairwise
4-state model. They reproduce the published independent-set counts (A291948, n = 3..10)
and maximal-independent-set counts (A292356, n = 3..9), and give the new A292356(10),
which also satisfies the congruences mod 2 and mod 5. There is no second independent
program for that term.

None of the techniques is new: this is transfer-matrix / pathwidth dynamic
programming, cutset conditioning and standard inclusion-exclusion for domination.
The contribution is applying them to a family that had only been brute-forced.

## Reproducing

Needs `clang` and Python 3 (standard library only). From `work/`:

```
clang -O3 -o pathdp3_3 -DNW=3 pathdp3.c
clang -O3 -o pathdp4_3 -DNW=3 pathdp4.c
python3 run4.py 10 22 8 check10      # A347480(10) by method 1, about 10 CPU-minutes
python3 run_elim.py 7 8 9 10         # A347480 by method 2 (n=9,10 need ~9 GB RAM)
python3 dom_elim.py 7 8 9 10         # A300529 by method 2
python3 symcheck.py                  # symmetry congruences
python3 gen_models.py maxindep 9 10  # A292356 by the generic method
```

`NOTEBOOK.md` is the working log, including the mistakes made along the way.

## Limits

- Method 1 costs roughly 2^37 state-visits at n=10 and 2^47 at n=11 and n=12.
  Method 2 cannot reach n >= 11, so terms beyond n=10 would rest on method 1 plus
  the congruence only.
- `pathdp*.c` do not handle isolated vertices (irrelevant here: minimum degree is 2).
