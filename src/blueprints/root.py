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

        # TODO: This should update the image to be the latest released version of the image
        result = subprocess.run(
            ["gcloud", "beta", "run", "jobs", "update", job_name, region_flag, f"--update-env-vars=DRAGONDROP_JOBID={request_json['job_run_id']}"],
            capture_output=True,
            text=True,
        )
        current_app.logger.info(result.stdout + "\n" + result.stderr)

        # Triggering the job to actually run
        result = subprocess.run(
            ["gcloud", "beta", "run", "jobs", "execute", job_name, f"--region={job_region}"],
            capture_output=True,
            text=True,
        )
        current_app.logger.info(result.stdout + "\n" + result.stderr)

        return "Cloud Run Job successfully triggered", 201
    except Exception as e:
        return f"Server Error: {e}", 500
