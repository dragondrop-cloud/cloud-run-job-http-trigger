"""
Root url app blueprint.
"""
import os
import subprocess
import yaml
from typing import Tuple
from flask import Blueprint, request, current_app

root = Blueprint("root", __name__)


@root.route("/", methods=["POST"])
def execute_cloud_run_job():
    """
    Execute the Cloud Run Job which is hosting the dragondrop.cloud
    core compute engine.
    """
    try:
        request_json = request.get_json()
        if "DRAGONDROP_JOBID" not in request_json:
            raise ValueError("Post request must contain a 'DRAGONDROP_JOBID'")

        job_name = os.getenv("JOB_NAME")
        job_region = os.getenv("JOB_REGION")
        region_flag = f"--region={job_region}"

        file_path_flag, _ = _generate_update_env_vars_file(request_json=request_json)

        current_app.logger.info(
            f"Updating the Cloud Run Job {job_name} in {job_region}"
        )
        result = subprocess.run(
            [
                "gcloud",
                "beta",
                "run",
                "jobs",
                "update",
                job_name,
                region_flag,
                file_path_flag,
            ],
            capture_output=True,
            text=True,
        )
        current_app.logger.info(
            f"Std. Out: {result.stdout}\nStd. Error: {result.stderr}"
        )

        # Triggering the job to actually run
        current_app.logger.info(
            f"Invoking the Cloud Run Job {job_name} in {job_region}"
        )
        result = subprocess.run(
            [
                "gcloud",
                "beta",
                "run",
                "jobs",
                "execute",
                job_name,
                f"--region={job_region}",
            ],
            capture_output=True,
            text=True,
        )
        current_app.logger.info(
            f"Std. Out: {result.stdout}\nStd. Error: {result.stderr}"
        )

        return "Cloud Run Job successfully triggered", 201
    except Exception as e:
        return f"Server Error: {e}", 500


def _generate_update_env_vars_file(request_json: dict) -> Tuple[str, dict]:
    """
    Helper function to generate the right string for the update-env-vars feature flag.
    """
    yml_file_path = "./env-vars.yml"
    env_var_flag = f"--env-vars-file={yml_file_path}"

    if "DRAGONDROP_JOBID" not in request_json:
        raise ValueError(
            "'DRAGONDROP_JOBID' must be included in the JSON body sent to this endpoint."
        )

    with open(yml_file_path, "w") as f:
        yaml.dump(request_json, f)

    return env_var_flag, request_json
