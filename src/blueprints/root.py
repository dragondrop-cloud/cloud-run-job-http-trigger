"""
Root url app blueprint.
"""
import os

import subprocess
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
                _generate_update_env_vars_string(request_json=request_json),
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


def _generate_update_env_vars_string(request_json: dict) -> str:
    """
    Helper function to generate the right string for the update-env-vars feature flag.
    """
    base_string = f"--update-env-vars=DRAGONDROP_JOBID={request_json['job_run_id']}"

    request_var_to_env_var = {
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

    for request_var in request_var_to_env_var.keys():
        if request_var in request_json:
            if request_var in {"migration_history_storage", "resource_white_list", "resource_black_list"}:
                base_string += f",DRAGONDROP_{request_var_to_env_var[request_var]}='{request_json[request_var]}'"
            else:
                base_string += f",DRAGONDROP_{request_var_to_env_var[request_var]}={request_json[request_var]}"

    return base_string
