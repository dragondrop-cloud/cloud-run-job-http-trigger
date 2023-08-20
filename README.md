# cloud-run-job-http-trigger
GCP Cloud Run service for triggering a GCP Cloud Run Job hosting the dragondrop engine.

## Purpose
Cloud Run Jobs are the easiest way to host the dragondrop.cloud core container. Unfortunately, it is
not possible to trigger a Cloud Run Job via an https request without getting an access token for a user or
service account with the permissions needed to execute the job.

At dragondrop.cloud, we always want to avoid having access to customer credentials of any kind (in fact even our
free tier offering is hosted in our customer's cloud environment), and so storing GCP credentials to then generate
an auth token is not an option.

Instead, we can make an https request to a Cloud Run-hosted service, which in turn handles executing the Cloud Run Job.

## Quick Start (with Terraform)
Our Terraform module for the dragondrop.cloud container also creates a Cloud Run Service in GCP that hosts this container.

The repository that defines this module can be found [here](https://github.com/dragondrop-cloud/terraform-google-dragondrop-compute).

## Quick Start (manual, not recommended)
1) Create a Cloud Run Job that hosts the [cloud-concierge](https://github.com/dragondrop-cloud/cloud-concierge) container.
2) Create a Cloud Run service that hosts the Flask application container created by this repository. The service account associated with the
Cloud Run service must have the IAM permissions to invoke Cloud Run routes for the Cloud Run Job from step 1.
3) Within the dragondrop Job that you have provisioned, specify the https url to be that of the Cloud Run service created as part of
step 2.

Now, dragondrop will handle scheduled or manual executions of the self-hosted engine, all without needing to store any credentials!

