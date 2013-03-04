import os
import qisys
from qisys import ui


def generate_coverage_xml_report(project):
    """ Generate a XML coverage report
    """
    bdir = project.build_directory
    sdir = project.path
    base_report = os.path.join(bdir, project.name + ".xml")
    ui.info(ui.green, "*", ui.reset, "Generate XML coverage report")
    cmd = ["gcovr",
            "--root", sdir,
            "--exclude", ".*test.*",
            "--exclude", ".*external.*",
            "--exclude", ".*example.*",
            "--xml",
            "--output", base_report]
    qisys.command.call(cmd, cwd=sdir, quiet=True)
