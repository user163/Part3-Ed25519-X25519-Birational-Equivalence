# Ed25519-X25519-Birational-Equivalence

The twisted Edwards curve *edwards25519* and the Montgomery curve *curve25519* are birationally equivalent, i.e. two points `M` and `N = n * M` of one curve can be transformed into two points of the other curve `M'` and `N' = n * M'` (note the unchanged `n` on both sides or `n' = n`). The formulas for the transformation in both directions can be found in [RFC 7748, chapter 4.1 Curve25519][1].

[1]: https://datatracker.ietf.org/doc/html/rfc7748#section-4.1

