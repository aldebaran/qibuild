import pytest

def clean_trad(proj):
    import os
    import qisys.sh
    pot_file = os.path.join(proj.path, "po", "translate.pot")
    fr_FR_po_file = os.path.join(proj.path, "po", "fr_FR.po")
    en_US_po_file = os.path.join(proj.path, "po", "en_US.po")
    qisys.sh.rm(en_US_po_file)
    qisys.sh.rm(fr_FR_po_file)
    qisys.sh.rm(pot_file)
    po_share = os.path.join(proj.path, "po", "share")
    qisys.sh.rm(po_share)

@pytest.fixture()
def toc(request):
    from qibuild.test.test_toc import TestToc
    test_toc = TestToc()
    request.addfinalizer(test_toc.clean)
    request.toc = test_toc.toc
    return test_toc.toc

@pytest.fixture()
def trad(request):
    import functools
    proj = request.toc.get_project("translate")
    clean_func = functools.partial(clean_trad, proj)
    clean_func()
    request.addfinalizer(clean_func)
    return proj

