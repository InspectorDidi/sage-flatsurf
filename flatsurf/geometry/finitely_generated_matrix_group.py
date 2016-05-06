r"""
Class for matrix groups generated by a finite number of elements.

.. TODO::

    - The stupid test ``_test_change_ring`` fails because if a matrix ``m`` is
      immutable then ``m.change_ring(m.base_ring())`` returns ``m`` and not a
      copy.

    - ``m.multiplicative_order()``

EXAMPLES::

    sage: from flatsurf.geometry.finitely_generated_matrix_group import  FinitelyGenerated2x2MatrixGroup

    sage: m1 = matrix([[1,1],[0,1]])
    sage: m2 = matrix([[1,0],[1,1]])
    sage: G = FinitelyGenerated2x2MatrixGroup([m1,m2])
    sage: G
    Matrix group generated by:
    [1 1]  [1 0]
    [0 1], [1 1]
    sage: it = iter(G)
    sage: [it.next() for _ in xrange(5)]
    [
    [1 0]  [1 1]  [1 2]  [2 1]  [ 0  1]
    [0 1], [0 1], [0 1], [1 1], [-1  1]
    ]

    sage: G = FinitelyGenerated2x2MatrixGroup([identity_matrix(2)])
"""

from sage.structure.parent import Parent
from sage.groups.group import Group
from sage.structure.sequence import Sequence
from sage.rings.infinity import Infinity
from sage.matrix.constructor import matrix

def matrix_multiplicative_order(m):
    r"""
    Return the order of the 2x2 matrix ``m``.
    """
    if m.det() != 1 and m.det() != -1:
        return Infinity

    # now we compute the potentially preserved quadratic form
    # i.e. looking for A such that m^t A m = A
    m00 = m[0,0]
    m01 = m[0,1]
    m10 = m[1,0]
    m11 = m[1,1]
    M = matrix(m.base_ring(),
        [[m00**2, m00*m10, m10**2],
         [m00*m01, m00*m11, m10*m11],
         [m01**2, m01*m11, m11**2]])

    # might there be several solutions ? (other than scaling)... should not
    try:
        v = (M-identity_matrix(3)).solve_right()
    except ValueError: # no solution
        return False

    raise NotImplementedError("your matrix is conjugate to an orthogonal matrix but the angle might not be rational.. to be terminated.")

    # then we conjugate and check if the angles are rational
    # we need to take a square root of a symmetric matrix... this is not implemented!
    A = matrix(m.base_ring(), [[v[0],v[1]],[v[1],v[2]]])


def invariant_quadratic_forms(m):
    r"""
    Return the space of quadratic forms invariant under m.

    If the matrix is orientable, there is only one (what about strange
    eigenvalues?)

    If the det(m) == -1 and trace(m) == 0, there are 2.

    EXAMPLES::

        sage: from flatsurf.geometry.finitely_generated_matrix_group import invariant_quadratic_forms

        sage: invariant_quadratic_forms(matrix(2, [0,1,-1,0]))
        Free module of degree 3 and rank 1 over Integer Ring
        Echelon basis matrix:
        [1 1 0]
        sage: invariant_quadratic_forms(matrix(2, [1,1,0,1]))
        Free module of degree 3 and rank 1 over Integer Ring
        Echelon basis matrix:
        [0 1 0]
        sage: invariant_quadratic_forms(matrix(2, [2,1,1,1]))
        Free module of degree 3 and rank 1 over Integer Ring
        Echelon basis matrix:
        [ 2 -2 -1]

        sage: r = matrix(2,[1,-1,1,0])
        sage: q = invariant_quadratic_forms(r)
        sage: q
        Free module of degree 3 and rank 1 over Integer Ring
        Echelon basis matrix:
        [ 2  2 -1]
        sage: a,c,b = q.gen()
        sage: m = matrix(2, [a,b,b,c])
        sage: r.transpose() * m * r == m
        True

        sage: invariant_quadratic_forms(matrix(2, [-1,0,0,1]))
        Free module of degree 3 and rank 2 over Integer Ring
        Echelon basis matrix:
        [1 0 0]
        [0 1 0]

        sage: invariant_quadratic_form(-identity_matrix(2))
        Traceback (most recent call last):
        ...
        ValueError: m must be non identity and non-singular

        sage: for _ in range(100):
        ....:     r = random_matrix(ZZ, 2, algorithm='unimodular')
        ....:     q = invariant_quadratic_forms(r)
        ....:     a,c,b = q.random_element()
        ....:     m = matrix(2, [a,b,b,c])
        ....:     assert r.transpose() * m * r == m
        ....:     m[0,0] = -m[0,0]
        ....:     m[0,1] = -m[0,1]
        ....:     q = invariant_quadratic_forms(r)
        ....:     a,c,b = q.random_element()
        ....:     m = matrix(2, [a,b,b,c])
        ....:     assert r.transpose() * m * r == m
    """
    if m.is_scalar():
        raise ValueError("m must be non scalar")
    s = m.det()
    if not s.is_unit():
        raise ValueError("determinant must be +1 or -1")
    a,b,c,d = m.list()
    V = matrix(m.base_ring(), 4, 3,
              [a-s*d,     0, (1+s)*c,
                 s*b,     c,  (1-s)*a,
                   b,   s*c,  (1-s)*d,
                   0,   d-s*a, (1+s)*b]
              ).right_kernel()
    return V

def contains_definite_form(V):
    r"""
    Check whether a given a subspace of the 3 dimensional space (a,b,c) contains
    a definitive positive quadratic form ax^2 + 2bxy + by^2.

    TESTS::

        sage: from flatsurf.geometry.finitely_generated_matrix_group import contains_definite_form

        sage: V = ZZ**3
        sage: W = V.submodule([(1,1,0)])
        sage: contains_definite_form(V.submodule([(1,1,0)]))
        True
        sage: contains_definite_form(V.submodule([(2,1,1)]))
        True
        sage: contains_definite_form(V.submodule([(1,1,1)]))
        False
        sage: contains_definite_form(V.submodule([(1,0,0),(0,1,0)]))
        True
        sage: contains_definite_form(V.submodule([(1,0,0),(0,0,1)]))
        False
    """
    dim = V.dimension()
    if dim == 0:
        return False
    elif dim == 1:
        a,c,b = V.gen(0)
        return b**2 < a*c
    elif dim == 2:
        a1,c1,b1 = V.gen(0)
        a2,c2,b2 = V.gen(1)
        if b1**2 < a1*c1 or b2**2 < a2*c2:
            return True
        return (2*b1*b2 - a2*c1 - a2*c1)**2 - 4 * (b1**2 - a1*c1) * a2*c2 > 0
    elif dim == 3:
        return True
    else:
        raise RuntimeError


class FinitelyGenerated2x2MatrixGroup(Group):
    r"""
    Finitely generated group of 2x2 matrices with real coefficients
    """
    def __init__(self, matrices, matrix_space=None, category=None):
        if matrix_space is None:
            from sage.matrix.matrix_space import MatrixSpace
            ring = Sequence(matrices).universe().base_ring()
            matrix_space = MatrixSpace(ring,2)

        self._generators = map(matrix_space,matrices)
        for m in self._generators:
            m.set_immutable()
        self._matrix_space = matrix_space

        if category is None:
            from sage.categories.groups import Groups
            category = Groups()

        Parent.__init__(self, category=category, facade=matrix_space)

    def is_abelian(self):
        r"""
        Check whether this group is abelian.

        .. TODO::

            move this method inside Sage

        EXAMPLES::
 

            sage: from flatsurf.geometry.finitely_generated_matrix_group import  FinitelyGenerated2x2MatrixGroup

            sage: m1 = matrix([[1,1],[0,1]])
            sage: m2 = matrix([[1,0],[1,1]])
            sage: G = FinitelyGenerated2x2MatrixGroup([m1,m2])
            sage: G.is_abelian()
            False

            sage: G = FinitelyGenerated2x2MatrixGroup([m1])
            sage: G.is_abelian()
            True
        """
        for a in self._generators:
            for b in self._generators:
                if a*b != b*a:
                    return False
        return True


    def _repr_(self):
        mat_string = [g.str().split('\n') for g in self._generators]
        return ("Matrix group generated by:\n" +
                "  ".join(x[0] for x in mat_string) + "\n" +
                ", ".join(x[1] for x in mat_string))

    def is_finite(self):
        r"""
        Is there a reasonable algorithm for 2x2 matrices ?

        A group is finite if and only if it is conjugate to a (finite) subgroup of O(2).

        EXAMPLES::

            sage: from flatsurf.geometry.finitely_generated_matrix_group import FinitelyGenerated2x2MatrixGroup
            sage: G = FinitelyGenerated2x2MatrixGroup([identity_matrix(2)])
            sage: G.is_finite()
            True

            sage: t = matrix(2, [2,1,1,1])

            sage: m1 = matrix([[0,1],[-1,0]])
            sage: m2 = matrix([[1,-1],[1,0]])
            sage: FinitelyGenerated2x2MatrixGroup([m1]).is_finite()
            True
            sage: FinitelyGenerated2x2MatrixGroup([t*m1*~t]).is_finite()
            True
            sage: FinitelyGenerated2x2MatrixGroup([m2]).is_finite()
            True
            sage: FinitelyGenerated2x2MatrixGroup([m1,m2]).is_finite()
            False
            sage: FinitelyGenerated2x2MatrixGroup([t*m1*~t,t*m2*~t]).is_finite()
            False

            sage: from flatsurf.geometry.polygon import number_field_elements_from_algebraics
            sage: c5 = QQbar.zeta(5).real()
            sage: s5 = QQbar.zeta(5).imag()
            sage: K, (c5,s5) = number_field_elements_from_algebraics([c5,s5])
            sage: r = matrix(K, 2, [c5,-s5,s5,c5])
            sage: FinitelyGenerated2x2MatrixGroup([m1,r]).is_finite()
            True
            sage: FinitelyGenerated2x2MatrixGroup([t*m1*~t,t*r*~t]).is_finite()
            True
            sage: FinitelyGenerated2x2MatrixGroup([m2,r]).is_finite()
            False
            sage: FinitelyGenerated2x2MatrixGroup([t*m2*~t, t*r*~t]).is_finite()
            False
        """
        # determinant and trace tests
        # (the code actually check that each generator is of finite order)
        for m in self._generators:
            if (m.det() != 1 and m.det() != -1) or \
               m.trace().abs() > 2 or \
               (m.trace().abs() == 2 and (m[0,1] or m[1,0])):
                   return False


        if len(self._generators) <= 1:
            return True

        # now we try to find a non-trivial invariant quadratic form
        from sage.modules.free_module import FreeModule
        V = FreeModule(self._matrix_space.base_ring(), 3)
        for g in self._generators:
            V = V.intersection(invariant_quadratic_forms(g))
            if not contains_definite_form(V):
                return False

        return True

    def cardinality(self):
        if self.is_finite():
            # THIS IS STUPID!!!
            return len(list(self))
        else:
            return Infinity

    def __iter__(self):
        yield self.one()
        s = set([self.one()])
        wait = self._generators[:]
        while wait:
            p = wait.pop(0)
            if p not in s:
                yield p
                s.add(p)
            for g in self._generators:
                for m in [p*g, p*g.inverse(), g*p, g.inverse()*p]:
                    m.set_immutable()
                    if m not in s:
                        yield m
                        s.add(m)
                        wait.append(m)

    def __eq__(self, other):
        return (isinstance(other, FinitelyGenerated2x2MatrixGroup) and
                self._generators == other._generators)

    def some_elements(self):
        from itertools import islice
        return list(islice(self, 5))

    def __ne__(self, other):
        return not self == other

    def __reduce__(self):
        return FinitelyGenerated2x2MatrixGroup, (self._generators, self._matrix_space)

    def one(self):
        return self._matrix_space.identity_matrix()

    def an_element(self):
        return self._generators[0]

    def gen(self, i):
        return self._generators[i]
