import os
import glob
import qibuild
from qibuild import ui

def generate_coverage_xml_report(project):
    """ Generate a XML coverage report
    """
    bdir = project.build_directory
    sdir = project.path
    base_report = os.path.join(bdir, project.name+".xml")
    ui.info(ui.green, "*", ui.reset, "Generate XML coverage report")
    cmd = [ 'gcovr',
            "-r", sdir,
            "-e", ".*test.*",
            "-e", ".*external.*",
            "-e", ".*example.*",
            "-x",
            "-o", base_report ]
    qibuild.command.call(cmd, quiet=True)

