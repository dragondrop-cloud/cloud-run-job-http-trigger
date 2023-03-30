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
        if "job_run_id" not in request_json:
            raise ValueError("Post request must contain a 'job_run_id'")

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

    request_var_to_env_var = {
        "job_run_id": "JOBID",
        "is_module_mode": "ISMODULEMODE",
        "migration_history_storage": "MIGRATIONHISTORYSTORAGE",
        "provider_versions": "PROVIDERS",
        "resource_white_list": "RESOURCEWHITELIST",
        "resource_black_list": "RESOURCEBLACKLIST",
        "reviewers": "PULLREVIEWERS",
        "s3_bucket_name": "S3BACKENDBUCKET",
        "state_backend": "STATEBACKEND",
        "terraform_cloud_organization_name": "TERRAFORMCLOUDORGANIZATION",
        "terraform_version": "TERRAFORMVERSION",
        "vcs_system": "VCSSYSTEM",
        "vcs_repo_name": "VCSREPO",
        "vcs_user": "VCSUSER",
        "vcs_base_branch": "VCSBASEBRANCH",
    }

    env_var_dict = {}

    for request_var in request_var_to_env_var.keys():
        if request_var in request_json:
            env_var_dict[
                f"DRAGONDROP_{request_var_to_env_var[request_var]}"
            ] = request_json[request_var]

    if "DRAGONDROP_JOBID" not in env_var_dict:
        raise ValueError(
            "'job_run_id' must be included in the JSON body sent to this endpoint."
        )

    with open(yml_file_path, "w") as f:
        yaml.dump(env_var_dict, f)

    return env_var_flag, env_var_dict
