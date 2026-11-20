# OEIS project notebook

Self-directed project on a MacBook lent by its owner (M5 Pro, 18 cores, 48 GB). Started 2026-11-16.

## Choosing a target

An earlier session left search dumps in `s1.json` and `search/` (OEIS entries with
keyword `more`, most recently changed first). I kept the OEIS default; nothing I'd
rather do came to mind that also gives a checkable result.

Considered and dropped:
- A326250 (weakly nesting graphs): carries "Conjecture: A006125(n) = a(n) + A000108(n)".
  I saw it is just antichains in the type-A root poset = Catalan. But a comment dated
  Nov 15 2026 in the entry already proves it. Nothing left to do.
- A324327, A284911, A372171, A326519, A317784, A290280, A281614: all extended in the
  last two days by very active contributors. No point racing.
- Famous `hard` ones (Dedekind numbers, Wieferich primes...): not laptop problems.

Chosen: **A347480, number of total dominating sets in the n-polygon diagonal
intersection graph**. Only 4 terms (n=3..6: 4, 24, 648, 263003), evidently from brute
force. The graphs are planar, so a dynamic programme over a narrow frontier should
reach much further than 2^N enumeration. Several sibling sequences on the same graphs
(A347920, A351590, A301340, ...) are equally short, so the machinery may transfer.

Definitions: graph = regular n-gon with all diagonals drawn; vertices are the polygon
vertices and all interior crossing points; edges are the segments between consecutive
points on each side/diagonal. A total dominating set S: every vertex (including those
in S) has a neighbour in S.

## Log

### Graph construction (`work/pdig.py`)
Floating-point intersections, merged with tolerance. Vertex counts for n=3..20 match
A007569 and edge counts match A135565, so concurrency (even n) is being detected right.

### Method 1: path DP (`work/pathdp.c`, `work/run_path.py`)
Process vertices in some order, deciding membership in S. State = one "already
dominated" bit for each vertex that has both processed and unprocessed neighbours.
When a vertex's last neighbour is processed it must be dominated. Exact multiword
integers, additions only.

- First run failed ("out of slots"): my width estimate ignored vertices that become
  active and retire in the same step. Fixed by mirroring the C allocation in Python.
- Reproduces the 4 known terms. Brute force (`work/brute.py`) also reproduces them.
- Random-graph test (`work/randtest.py`): 300 random graphs, random orders, vs brute
  force. All 203 graphs without isolated vertices agree. The 97 mismatches all have an
  isolated vertex, which the DP never checks (answer should be 0). Not relevant here
  (min degree 2) but it is a real limitation of the code.
- New: a(7) = 793290313945, a(8) = 19780521126498508 (to be confirmed by method 2).
- Widths found by greedy/sweep orders: n=9: 28 bits, n=10: 33, n=11: 42, n=12: 44.
  So this method stops at n=9; n>=10 needs a tree decomposition.
- a(9) by method 1 (unconditioned, 28 bits, 13 GB, 28 s): 127122812445017255670206773047466222123.

### Splitting the big runs (`work/pathdp2.c`, later `pathdp3.c`)
Memory, not time, is what stops method 1 at n=10 (33 bits). Trick: pick a set C of
vertices and apply inclusion-exclusion only to them:

    #TDS = sum over T subset of C of (-1)^|T| * #{S : every vertex outside C is dominated,
                                                  and no neighbour of T is in S}

C-vertices then need no state bit, at the cost of 2^|C| independent (parallel) runs.
Verified against brute force on 183 random graphs, including C = everything.

**Mistake 1.** I assumed conditioning was free in time (each bit removed halves
memory and doubles the number of runs). It is only free for vertices that hold a slot
through the *whole* run. My first rule picked whatever vertices were active at the
peak step; with a line-sweep order those are short-lived, and n=9 went from 2^31.9 to
2^37.5 state-visits (28 s -> 100 s on 14 cores, worse than not splitting at all).
Fix (`work/condplan.py`): use an *angular* sweep about the centre. The vertices on the
starting ray stay active until the sweep comes back round, so conditioning on them
costs nothing. n=10 becomes 2^37.4 work at 22 bits of state.

**Mistake 2.** `pathdp3.c` (single array, skips freshly allocated bits) had a
double-count: in the branch with no new neighbours I added A[t] twice. The random
test caught it on the first run (all mismatches too large). Fixed; 183/183 agree.

Order annealing (`work/anneal.py`) and off-centre pivots (`work/pivot.py`) gained
under one bit; the centred angular sweep is essentially as good as I can find.

### Method 2: variable elimination (`work/elimdp.c`, `work/run_elim.py`)
Deliberately different formulation, for an independent check. Full
inclusion-exclusion over the set T of undominated vertices gives

    #TDS = sum over (S,T) of (-1)^|T| * prod over edges uv of [not(t_u & s_v)] [not(t_v & s_u)]

a pairwise 4-state model on G, evaluated by eliminating vertices along a min-fill
order (width 15 for n=9, 10), modulo 62-bit primes, CRT with one prime more than
needed and a range check (result must be < 2^N). 150 random graphs agree with brute
force (this method also handles isolated vertices).

### Results so far
| n | a(n) | how checked |
|---|------|-------------|
| 3..6 | 4, 24, 648, 263003 | known terms; brute force, method 1, method 2 |
| 7 | 793290313945 | method 1 (3 orders/splittings), method 2 |
| 8 | 19780521126498508 | method 1 (3 orders/splittings), method 2 |
| 9 | 127122812445017255670206773047466222123 | method 1 unsplit, split two ways; method 2 with 4 primes |
| 10 | 4445417218586525760827112474487874053620425707538 | method 1 split (61 s); method 2 with 4 primes |

Method 2 cannot reach n=11 (width 25 -> 4^25 table) or n=12 (width 21), so those
will rest on method 1 alone, run with two different plans if time allows.

### Long runs
n=11: N=341, |C|=17, 25 bits of state, est. 2^46.9 state-visits, 1024 resumable chunks
(`work/res_n11a.jsonl`), 14 processes. Launched 2026-11-16 evening.
Restart with: `cd work && nohup caffeinate -i python3 launch.py 11 25 14 n11a 10 > n11a.log 2>&1 &`

### Third check: rotational symmetry (`work/symcheck.py`, `work/symres.py`)
If g is a rotation of prime order p, the group <g> acts on the solution sets and every
non-fixed orbit has size p, so a(n) == #(g-invariant solutions) (mod p). Invariant
solutions are solutions on the quotient graph (an orbit that contains an edge gets a
loop: it dominates itself). The quotient is small, so this is a cheap, structurally
unrelated computation. It passes for every known and new term (n=3..10, all prime
p | n, both sequences). It is the only independent check available at n=11, 12:

    n=11: TDS == 8 (mod 11),  dominating sets == 0 (mod 11)
    n=12: TDS == 2 (mod 3),   dominating sets == 1 (mod 3)     (p=2 quotient too wide)

A wrong answer passes with probability about 1/p, so this is weak for n=12.

### Sibling sequence A300529 (dominating sets), 2026-11-16
Listing every entry on this graph family (`search2/`) showed A300529 has 5 terms.
A dominating set is a total dominating set of the graph with a loop at every vertex,
so both methods carry over (`work/dom_elim.py`; `work/pathdp4.c` + `work/dom_path.py`,
162 random loop-graphs agree with brute force). Both reproduce the 5 published terms
7, 27, 863, 385063, 1993292588087 (a(7) is someone else's computation, a good sign).

| n | A300529(n) | how checked |
|---|-----------|-------------|
| 8 | 54230068320039879 | methods 1 and 2, symmetry mod 2 |
| 9 | 2773576274509432974802491946402927554739 | methods 1 and 2, symmetry mod 3 |
| 10 | 119283874191819442231697481474634239320305447119279 | methods 1 and 2, symmetry mod 2, 5 |

### Long-run queue (`work/queue.sh`), started 2026-11-16 evening
Measured 10.4 s per conditioning mask for n=11 -> 2^17 masks -> about 27 h on 14
processes. Queue order: TDS n=11 (`n11a`), TDS n=12 (`n12a`), dominating sets n=11
(`d11a`), n=12 (`d12a`); each roughly a day. Everything is chunked and resumable:
re-run `nohup ./queue.sh > queue.log 2>&1 &` from `work/` after a reboot. Results land
in `work/result_<tag>.txt`; progress in `work/<tag>.log`.

### Change of plan, 2026-11-16 22:55
- OEIS policy ("Use of AI for OEIS Submissions"): needs a human author who understands
  and has verified the work; AI cannot be named as author. The owner is busy and will not
  submit or email the editors, and I did not want them to. So no publication for now;
  the aim is a clean, re-verifiable write-up in this folder.
- The owner needs the laptop: no multi-day runs. Keep compute to windows of a few hours,
  or overnight when the owner says so. The 4-stage queue (`queue.sh`) is cancelled; n=12 and
  the dominating-set long runs are dropped unless more nights are offered.
- n=11 (A347480) continues in bounded windows with `work/night.sh <procs> <stop HH:MM>`.
  140/1024 chunks were done at 22:55; tonight's window runs 16 processes until 07:00
  (expect roughly 430/1024 by then). About two more nights needed. Ask the owner before
  starting each window.

### Overnight side job: generic model + A292356, 2026-11-16 late
With the laptop mostly busy on n=11, I generalised method 2 (`work/elimgen.c`,
`work/gen_models.py`): any symmetric pairwise model with 4 states per vertex, given
as 4 vertex weights and a 4x4 edge matrix. Models: independent sets, maximal
independent sets (independent, plus inclusion-exclusion over undominated outsiders),
and total dominating sets again as a regression.

- 120 random graphs across the three models agree with brute force.
- Independent sets reproduce A291948 for n=3..10, including the published
  a(10) = 83148730861613724622207922410 (same width-15 tables as the new term).
- Maximal independent sets reproduce all 7 published terms of A292356 (n=3..9).
- Total dominating sets via the generic code reproduce a(7), a(8), a(10).
- **New: A292356(10) = 1272369852811691513.** Symmetry congruences hold mod 2 and
  mod 5 (`work/gen_sym.py`), and for every earlier term.

Honest status of that term: one counting method only (variable elimination), plus
the congruences and the full-scale validations above. No second independent program,
unlike the A347480 / A300529 terms. n=11 is out of reach for this method (width 25).

### 2026-11-19: state, and a fourth check (mirror symmetry, `work/refl.py`)
- n=11 stood at 508/1024 chunks after the earlier windows. Started a light daytime window
  (8 processes, stops 14:30). About 13 hours of 16-process time remain.
- `.gitignore` now covers `work/elimgen_*`; the four compiled binaries are untracked.
- Looked for a second independent program for A292356(10). A direct path DP needs 3 states
  per frontier vertex (3^33 at n=10), and a formulation without inclusion-exclusion has
  elimination width 41+. Neither is feasible, so that term stays on one program.
- New check: a reflection is an automorphism of order 2, so a(n) is congruent mod 2 to the
  count on the reflection quotient (width only 12 at n=11). Passes for every known and new
  term of A347480 and A300529 (n=3..10, both mirror classes for even n) and for A292356(10).
  Dominating sets always come out odd, as a known theorem says they must.
- Prediction for the running job: A347480(11) is even. With the rotation check that is
  **A347480(11) == 8 (mod 22)**, so a wrong answer now passes with probability about 1/22.

### 2026-11-19 afternoon: owner away for a week, laptop left behind
The owner said the machine is free all week for benign work. The few-hour limit existed
because they needed the laptop, so it is lifted until they are back. `work/queue.sh` now
runs continuously on 16 processes: A347480(11) (692/1024 at restart), then A300529(11),
then n=12 for both. Restart after a reboot: `cd work && nohup ./queue.sh > queue.log 2>&1 &`.
Expected checks: A347480(11) == 8 (mod 22); A300529(11) == 11 (mod 22) (0 mod 11, and odd).

### 2026-11-19, later: plan reversed
The owner is taking the laptop after all and may need it for interviews. Queue stopped by
hand; the few-hour limit and ask-before-long-runs rule apply again. Nothing is lost (chunks
are resumable). Resume n=11 only with a bounded window: `cd work && ./night.sh <procs> <HH:MM>`.
