# Ed25519-X25519-Birational-Equivalence

The twisted Edwards curve *edwards25519* and the Montgomery curve *curve25519* are birationally equivalent, i.e. two points `M` and `N = n * M` of one curve can be transformed into two points of the other curve `M'` and `N' = n * M'` (note the unchanged `n` on both sides or `n' = n`). The formulas for the transformation in both directions can be found in [RFC 7748, chapter 4.1 Curve25519][1].

This is illustrated in the first test (*Main test 1*) in *100_birational_equivaleny.py*.

--------------

Conversion of an Ed25519 key pair to an X25519 key pair is possible as follows:

- Hash the secret 32 bytes Ed25519 key with SHA512 and use the first 32 bytes. These are clamped (`s_clamped`). The result, `s_clamped`, is the secret X25519 key.
- Decompress the public 32 bytes Ed25519 key, i.e. reconstruct the full x and y coordinates from the y coordinate (and the sign of the x coordinate). Transform the point on the ewards25519 curve to the corresponding point on the curve25519 curve. The public X25519 key is the x coordinate.  
Consistency test: the same point on the curve25519 curve is obtained when the secret X25519 key is multiplied by the curve25519 generator point and the x coordinate of the resulting point is used.

This is demonstrated in the second test (*Main test 2*) in *100_birational_equivaleny.py*.

[1]: https://datatracker.ietf.org/doc/html/rfc7748#section-4.1

