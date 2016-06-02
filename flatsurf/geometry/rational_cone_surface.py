from flatsurf.geometry.cone_surface import ConeSurface
from flatsurf.geometry.matrix_2x2 import is_cosine_sine_of_rational
class RationalConeSurface(ConeSurface):
    r"""
    A Euclidean cone surface whose cone angles are all rational multiples of pi.
    """
    def _test_edge_matrix(self, **options):
        r"""
        Check the compatibility condition
        """
        tester = self._tester(**options)

        from flatsurf.geometry.similarity_surface import SimilaritySurface
        if self.is_finite():
            it = self.label_iterator()
        else:
            from itertools import islice
            it = islice(self.label_iterator(), 30)

        for lab in it:
            p = self.polygon(lab)
            for e in xrange(p.num_edges()):
                # Warning: check the matrices computed from the edges,
                # rather the ones overriden by TranslationSurface.
                m = SimilaritySurface.edge_matrix(self,lab,e)
                tester.assertTrue(is_cosine_sine_of_rational(m[0][0],m[0][1]))

