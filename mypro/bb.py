"""Bb模块的文档注释"""


class Bb(object):
    """
    Bb类的注释
    """

    @staticmethod
    def bb_api(x, y):
        """
        求商
        >>> Bb.bb_api(2, 4)
        0.5
        >>> Bb.bb_api(4, 2)
        2.0
        """
        return x / y