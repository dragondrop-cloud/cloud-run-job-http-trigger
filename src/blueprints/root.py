"""
Root url app blueprint.
"""
import os

import requests
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
        # TODO: Retrieve access token from Cloud Run Service Account via the metadata server
        if "job_run_id" not in request_json:
            raise ValueError("Post request must contain a 'job_run_id'")

        # TODO: Should be fine, as long as the cloud run instance is in the same project and
        # TODO: region as the job itself.
        job_name = os.getenv("JOB_NAME")

        # TODO: Can gcloud be run in the container and authenticate successfully? The answer looks to be yes!
        # TODO: Make HTTPS request to update the Cloud Run job to have a new env variable value
        # TODO: for DRAGONDROP_JOBID. This is necessary since the execution body must itself be empty and cannot
        # TODO: pass variables directly.

        # TODO: Also should update the image to be the latest image
        result = subprocess.run(
            ["gcloud", "beta", "run", "jobs", "update", job_name, f"--update-env-vars=DRAGONDROP_JOBID={request_json['job_run_id']}"],
            capture_output=True,
            text=True,
        )
        current_app.logger.info(result.stdout + "\n" + result.stderr)

        # Triggering the job to actually run
        result = subprocess.run(
            ["gcloud", "beta", "run", "jobs", "execute", job_name],
            capture_output=True,
            text=True,
        )
        current_app.logger.info(result.stdout + "\n" + result.stderr)

        return "Cloud Run Job successfully triggered", 201
    except Exception as e:
        return f"Server Error: {e}", 500
