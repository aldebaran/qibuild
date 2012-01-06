qibuild.dependencies_solver -- Resolving dependencies
=====================================================

.. py:module:: qibuild.dependencies_solver


DependenciesSolver
------------------


.. py:class:: DependenciesSolver(projects, packages)

    Projects and packages should have the following attributes:
      * ``name``     a name
      * ``depends``  a list of build dependencies
      * ``rdepends`` a list of runtime dependencies


    Resolve dependencies between projects a packages


    .. py:method:: solve(names[, runtime=False])

        Given a list of names, try to sort them in the correct order.

        :param names:   a list of projects to build
        :param runtime: True if using runtime dependencies

        Return (projects, packages, not_found) where:
           * projects  is a list of project names
           * packages  is a list of packages names
           * not_found is a list of names that were not found

        The solving is a bit tricky: the idea is that the list of projects
        retruned is the list of projects that have to be built.

        So for instance, assuiming the 'hello' always depends on 'world'

          * Projects=['hello', 'world'], packages = [] , names=['hello]'  -> projects = ['hello', 'world]
          * Projects=['hello'], packages = ['world'], names=['hello]'  -> projects = ['hello']
          * Projects=['hello', 'world'], packages = ['world'] , names=['hello]'  -> projects = ['hello', 'world]

        But, you can force using the 'world' from sources if you specify add
        'world' to the list of project names:

          * Projects=['hello', 'world'], packages = ['world'] , names=['hello', 'world']  -> projects = ['hello', 'world]



