# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
App that launches a folder browser from inside of Shotgun
"""

import tank
import sys
import os
import sgtk


class LaunchFolder(tank.platform.Application):

    def init_app(self):
        entity_types = self.get_setting("entity_types")
        deny_permissions = self.get_setting("deny_permissions")
        deny_platforms = self.get_setting("deny_platforms")

        p = {
            "title": "Open Folders(s)",
            "deny_permissions": deny_permissions,
            "deny_platforms": deny_platforms,
            "supports_multiple_selection": True
        }

        self.engine.register_command("show_in_filesystem", self.show_in_filesystem, p)

        q = {
            "title": "Show Path(s)",
            "deny_permissions": deny_permissions,
            "deny_platforms": deny_platforms,
            "supports_multiple_selection": True
        }

        self.engine.register_command("show_paths", self.show_paths, q)

    def launch(self, path):
        self.log_debug("Launching file system viewer for folder %s" % path)

        # get the setting
        system = sys.platform

        # run the app
        if system == "linux2":
            cmd = 'xdg-open "%s"' % path
        elif system == "darwin":
            cmd = 'open "%s"' % path
        elif system == "win32":
            cmd = 'cmd.exe /C start "Folder" "%s"' % path
        else:
            raise Exception("Platform '%s' is not supported." % system)

        self.log_debug("Executing command '%s'" % cmd)
        exit_code = os.system(cmd)
        if exit_code != 0:
            self.log_error("Failed to launch '%s'!" % cmd)

    def show_in_filesystem(self, entity_type, entity_ids):
        """
        Pop up a filesystem finder window for each folder associated
        with the given entity ids.
        """
        try:
            paths = []

            for eid in entity_ids:
                # Use the path cache to look up all paths linked to the task's entity
                paths.extend(self.get_paths(entity_type, eid))

            if len(paths) == 0:
                self.log_info("No location exists on disk yet for any of the selected entities. "
                              "Please use shotgun to create folders and then try again!")
            else:
                # launch folder windows
                for x in paths:
                    self.launch(x)
        except Exception as e:
            self.log_info(str(e))

    def show_paths(self, entity_type, entity_ids):
        """
        Pop up a filesystem finder window for each folder associated
        with the given entity ids.
        """
        try:
            paths = []

            for eid in entity_ids:
                # Use the path cache to look up all paths linked to the task's entity
                paths.extend(self.get_paths(entity_type, eid, directory=False))

            if len(paths) == 0:
                self.log_info("No location exists on disk yet for any of the selected entities. "
                              "Please use shotgun to create folders and then try again!")
            else:
                for p in paths:
                    p.replace("\\", "\\\\")
                self.log_info("\n".join(paths))
        except Exception as e:
            self.log_info(str(e))

    def get_paths(self, entity_type, eid, directory=True):
        self.log_info(str(entity_type) + "\n")
        published_files = []
        paths = []
        looker = self.tank.shotgun
        if entity_type == "Version":
            versions = looker.find("Version", [['id', 'is', eid]])
            for version in versions:
                pfs = looker.find("PublishedFile", [['version', 'is', version]], ['path', 'sg_publish_path'])
                published_files.extend(pfs)
        elif entity_type == "PublishedFile":
            published_files.extend(looker.find("PublishedFile", [['id', 'is', eid]], ['path', 'sg_publish_path']))
        for published_file in published_files:
            path_obj = published_file.get("path")
            published_path_obj = published_file.get("sg_publish_path")
            path = None
            if published_path_obj and published_path_obj.get("local_path"):
                if directory:
                    path = os.path.dirname(published_path_obj.get("local_path"))
                else:
                    path = published_path_obj.get("local_path")
            if not path and path_obj and path_obj.get("local_path"):
                if directory:
                    path = os.path.dirname(path_obj.get("local_path"))
                else:
                    path = path_obj.get("local_path")
            if path:
                paths.append(path)


        return paths
