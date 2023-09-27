# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import logging
from typing import Any
from typing import Dict
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import HookCallResult
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.execution_results import StepResult
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder

log = logging.getLogger(__name__)

JOB_RUN_SUMMARY_FILE_PATH = "JOB_RUN_SUMMARY_FILE_PATH"


class JobRunSummaryOutputPlugin:
    @hookimpl
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        config_builder.add(
            key=JOB_RUN_SUMMARY_FILE_PATH,
            default_value="",
            description="The path location of the file where job run result summary is stored.",
        )

    @hookimpl(hookwrapper=True)
    def run_job(self, context: JobContext) -> None:
        out: HookCallResult
        out = yield

        output_path = context.core_context.configuration.get_value(
            JOB_RUN_SUMMARY_FILE_PATH
        )
        if output_path:
            log.debug(
                f"Summary output path is {output_path}. Will save job run summary there."
            )
            summary_infos = self._collect_job_summary(out.get_result())
            self._write_summary_to_file(summary_infos, output_path)

    @staticmethod
    def _write_summary_to_file(summary: dict[str, Any], output_path: str) -> None:
        with open(output_path, "w") as outfile:
            outfile.write(json.dumps(summary))

    @staticmethod
    def _collect_job_summary(result: ExecutionResult) -> dict[str, Any]:
        job_summary = {}
        infos = []
        for step_result in result.steps_list:
            info = {
                "step_name": step_result.name,
                "status": str(step_result.status.name),
                "blamee": step_result.blamee.name if step_result.blamee else None,
                "details": step_result.details,
            }
            infos.append(info)
        job_summary["steps"] = infos
        job_summary["status"] = str(result.status.name)
        job_summary["blamee"] = (
            result.get_blamee().name if result.get_blamee() else None
        )
        job_summary["details"] = result.get_details()
        return job_summary
