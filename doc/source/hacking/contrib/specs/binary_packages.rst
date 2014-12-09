Toolchain binary packages
==========================

XML syntax
-----------


Feeds
++++++

.. code-block:: xml

  <toolchain>
    <!-- A normal package, for retro-compat -->
    <package name="foo" version="0.2" url="http://foo.zip" />
    <!-- A svn package without revision: use latest revision -->
    <package name="libqi" url="svn://toolchains/linux64/trunk/packages/libqi" />
    <!-- Can specify revision if necessary -->
    <package name="gtest" url="svn://toolchains/linux64/trunk/package/libgtest" revision="42" />
  </toolchain>


Toolchain database
+++++++++++++++++++

.. code-block:: xml

  <!-- in ~/.config/qi/toolchains/name.xml -->
  <toolchain feed="http://feed.xml">
    <!-- a normal remote package -->
    <package name="foo" version="0.2" path="..." />

    <!-- svn packages -->
    <package name="libqi" svn="true" path="..." />
    <package name="gtest" svn="true" revision="42" path="..." />

    <!-- a local package (for public ctcs and sdks) -->
    <package name="ctc" path="/path/to/ctc" toolchain_file="cross-config.cmake" />

    <local>
      <!-- created by running qitoolchain remove-package -c name qt -->
      <removed>
        <package name="qt" />
      </removed>
      <!-- created by running qitoolchain import-package -->
      <added>
        <package name="oracle-jdk" path="..." />
      </added>
    </local>
  </toolchain>


Implementation
+++++++++++++++

.. code-block:: python

    class QiPackage():
        def __init__(self):
            self.path = None # can be none when not in a db
            self.name
            self.url
            self.build_depends
            self.run_depends
            self.test_depends
            self.load()

        def install(self, components=None):
            if components:
                for component in components:
                    # read install_<component>_manifest.txt if it exists
                    # read mask_<component> if it exists

        def load(self):
            # read package.xml if it exists, set build_depends, run_depends, test_depends

    class SvnPackage(QiPackage):
        def __init__(self):
            self.revision = None

        def update(self):
            if self.revsion:
                "svn up -r self.revsion"
            else:
                "svn up"

        def checkout(self):
            ...


    class FeedParser():
        def parse_feed(feed_locations):
            return packages

    class ToolchainDatabase():
        def __init__(self, name):
              self.path
              self.name
              self.packages = dict()
              self.local_packages = dict()

        def update(self, feed_url):
            parser = ...
            remote_packages = parser.parse_feed(feed_url)
            for remote_package in remote_packages:
                to_add = ..
                to_remove = ...

            # set package.path (after download or svn checkout)

            for svn_package in svn_packages:
                svn_package.update()

        def add(self, package):
            pass

        def remove(self, package_name):
            pass


        def solve_deps(self, package_names):
            for package in self.packages:
                package.load()
            qisys.sort.topo_sort(....)
            return packages


        # in qibuild.actions.make_package
        def make_package():
            project.install(tmpdir, components=["test", "runtime", "devel"]
            write_manifests()
            write_qipackage_xml()

        # in qibuildfarm.make_package

        toolchain.update()
        make_package()
        # copy package to db
        # svn commit_all

