## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Synchronize local and remote profiles

"""

from qisys import ui
import qibuild.profile

def sync_build_profiles(worktree, xml_path):
    """ Sync a worktree by reading new profiles from a manifest

    """
    ui.info(ui.green, "Synchronizing build profiles ...")
    local_xml = worktree.qibuild_xml
    remote_xml = xml_path
    local = qibuild.profile.parse_profiles(local_xml)
    remote = qibuild.profile.parse_profiles(remote_xml)
    new_profiles, updated_profiles = _compute_updates(local, remote)
    for new_profile in new_profiles:
        ui.info(ui.green, " * New:", ui.blue, new_profile.name)
        qibuild.profile.add_profile(local_xml, new_profile)
    if updated_profiles:
        mess = "The following profiles have been updated:\n"
        for updated_profile in updated_profiles:
            mess += "  * " + updated_profile.name + "\n"
        ui.warning(mess)


def _compute_updates(local_profiles, remote_profiles):
    """ Compare a local set of profiles with a remote set.

    Return a list of profiles to add, and a list of profiles
    that have been updated.

    """
    # Note: no profile will ever be removed, I guess we don't care
    new = list()
    updated = list()
    for remote_profile in remote_profiles.values():
        if remote_profile.name in local_profiles:
            local_profile = local_profiles.get(remote_profile.name)
            if local_profile != remote_profile:
                updated.append(remote_profile)
        else:
            new.append(remote_profile)
    return new, updated
