"""Miscellaneous utilities"""

def run_doctest(module_name, **extraglobs):
    import doctest
    from sys import modules

    doctest.testmod(
        modules[module_name],
        extraglobs=extraglobs,
        verbose=1,
    )
