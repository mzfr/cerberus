import abc
import os
import shutil
from datetime import datetime
from os.path import join
from typing import Any
from typing import Dict
from typing import List

from app.core import container
from app.core import definitions
from app.core import utilities
from app.core.task.stats.RepairToolStats import RepairToolStats
from app.core.task.typing.DirectoryInfo import DirectoryInfo
from app.core.utilities import error_exit
from app.drivers.tools.AbstractTool import AbstractTool


class AbstractRepairTool(AbstractTool):
    key_bin_path = definitions.KEY_BINARY_PATH
    key_crash_cmd = definitions.KEY_CRASH_CMD
    key_exploit_list = definitions.KEY_EXPLOIT_LIST
    key_fix_file = definitions.KEY_FIX_FILE
    key_fix_file_list = definitions.KEY_FIX_FILE_LIST
    key_fix_lines = definitions.KEY_FIX_LINES
    key_fix_loc = definitions.KEY_FIX_LOC
    key_java_version = definitions.KEY_JAVA_VERSION
    key_config_timeout_test = definitions.KEY_CONFIG_TIMEOUT_TESTCASE
    key_dependencies = definitions.KEY_DEPENDENCIES
    stats: RepairToolStats

    def __init__(self, tool_name: str) -> None:
        self.stats = RepairToolStats()
        self.tool_type = "repair-tool"
        super().__init__(tool_name)

    def analyse_output(
        self, dir_info: DirectoryInfo, bug_id: str, fail_list: List[str]
    ) -> RepairToolStats:
        """
        analyse tool output and collect information
        output of the tool is logged at self.log_output_path
        information required to be extracted are:

            self.stats.patches_stats.non_compilable
            self.stats.patches_stats.plausible
            self.stats.patches_stats.size
            self.stats.patches_stats.enumerations
            self.stats.patches_stats.generated

            self.stats.time_stats.total_validation
            self.stats.time_stats.total_build
            self.stats.time_stats.timestamp_compilation
            self.stats.time_stats.timestamp_validation
            self.stats.time_stats.timestamp_plausible
        """

        if self.is_dir(self.dir_patch):
            self.stats.patch_stats.generated = len(self.list_dir(self.dir_patch))

        return self.stats

    def save_artifacts(self, dir_info: Dict[str, str]) -> None:
        """
        Save useful artifacts from the repair execution
        output folder -> self.dir_output
        logs folder -> self.dir_logs
        The parent method should be invoked at last to archive the results
        """
        base_dir_patches = dir_info.get("patches", "")
        if os.path.isdir(base_dir_patches):
            dir_patches = join(base_dir_patches, self.name)
            if os.path.isdir(dir_patches):
                shutil.rmtree(dir_patches)
            if self.container_id:
                container.copy_file_from_container(
                    self.container_id, self.dir_patch, dir_patches
                )
            else:
                if self.dir_patch != "":
                    save_command = "cp -rf {} {};".format(self.dir_patch, dir_patches)
                    utilities.execute_command(save_command)

        super().save_artifacts(dir_info)
        return
