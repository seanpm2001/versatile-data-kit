# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import structlog as log
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    log.info("Step 1.")
    job_input.execute_template("cancel-job", {})
