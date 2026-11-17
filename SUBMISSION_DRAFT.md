# Draft OEIS contributions (not submitted)

Submitting needs an OEIS account and a human decision about attribution, so nothing
has been sent. OEIS editors expect contributors to say how terms were obtained; these
were computed by Claude (an AI model made by Anthropic) on a laptop lent by its owner, with
the checks listed in NOTEBOOK.md. Whoever submits should say so.

**Policy check (2026-11-16):** the OEIS wiki page "Use of AI for OEIS Submissions"
requires a human author who has verified the terms and understands any AI-written
program, forbids naming an AI as author or co-author, and forbids AI-generated comment
text. So these drafts cannot simply be pasted in by someone who has not checked the
work. See NOTEBOOK.md / the conversation for options.

## A347480  Number of total dominating sets in the n-polygon diagonal intersection graph

Current DATA: 4, 24, 648, 263003

Proposed DATA:
4, 24, 648, 263003, 793290313945, 19780521126498508, 127122812445017255670206773047466222123, 4445417218586525760827112474487874053620425707538

Proposed EXTENSIONS line:  a(7)-a(10) from ...

Proposed COMMENT (optional):
For a rotation of prime order p dividing n, a(n) is congruent mod p to the number of
total dominating sets of the quotient graph (with loops), which gives an independent
check of the terms.

## A300529  Number of dominating sets in the n-polygon diagonal intersection graph

Current DATA: 7, 27, 863, 385063, 1993292588087

Proposed DATA:
7, 27, 863, 385063, 1993292588087, 54230068320039879, 2773576274509432974802491946402927554739, 119283874191819442231697481474634239320305447119279

Proposed EXTENSIONS line:  a(8)-a(10) from ...

## Method (for the submission comment / a linked text file)
Vertex-ordering dynamic programme with one "dominated" bit per frontier vertex, using
an angular sweep of the planar drawing; memory reduced by inclusion-exclusion over the
vertices on the starting ray. Cross-checked by variable elimination on the signed
pairwise model  sum_{S,T} (-1)^|T| prod_{uv in E} [not(t_u s_v)][not(t_v s_u)]
modulo several 62-bit primes. Source in work/.

## Pending
a(11), a(12) of both sequences are being computed (see NOTEBOOK.md, "Long-run queue").
These will have only the symmetry congruence as an independent check.
