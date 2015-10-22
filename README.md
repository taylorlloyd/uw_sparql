# uw_sparql

This code reflects efforts to deduplicate data found in RDF data by matching subjects in
(Subject, Predicate, Object) tuples.

Because pairwise comparisons are expensive, the algorithm works as follows:

create an empty hashmap M
for each unique predicate p:
    for each tuple (s, pred, o) where pred = p:
        M[hash(o)] += s
    for each list l in M:
        if size(l) < sqrt(all entries) && size(l) > 1:
            pairwise-compare all subjects in l

For pairwise comparisons, we use a weighted edit distance formula.
Our comparison functions were not yet well explored, and need more work.
