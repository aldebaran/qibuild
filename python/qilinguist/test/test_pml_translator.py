## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
from qilinguist.pml_translator import translations_files_from_pml

def test_parse_pml(tmpdir):
    pml_path = tmpdir.join("foo.pml")
    pml_path.write("""
<Package name="foo" format_version="4">
  <Translations>
    <Translation name="foo_fr_FR"
                 src="translations/foo_fr_FR.ts"
                 language="fr_FR" />
    <Translation name="foo_en_US"
                 src="translations/foo_en_US.ts"
                 language="en_US" />
  </Translations>

</Package>
""")
    translations = translations_files_from_pml(pml_path.strpath)
    assert translations == ["translations/foo_fr_FR.ts",
                            "translations/foo_en_US.ts"]
