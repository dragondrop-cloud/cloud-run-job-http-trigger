"""Unit tests for helper functions within the root blueprint"""
from unittest import TestCase
from src.blueprints.root import _generate_update_env_vars_string


def test_generate_update_env_vars_string():
    """Unit test for the _generate_update_env_vars_string"""
    case = TestCase()

    input_request_json_no_other_vars = {"job_run_id": "my_id"}

    input_request_json_one_other_var = {
        "job_run_id": "my_id",
        "resource_black_list": """["google_storage_bucket","aws_vpc"]""",
    }

    input_request_json_all_vars = {
        "job_run_id": "my_id",
        "resource_white_list": """["google_example_resource"]""",
        "resource_black_list": """["google_storage_bucket","aws_vpc"]""",
        "is_module_mode": "True",
    }

    case.assertEqual(
        _generate_update_env_vars_string(input_request_json_no_other_vars),
        "--update-env-vars=DRAGONDROP_JOBID=my_id",
    )

    case.assertEqual(
        _generate_update_env_vars_string(input_request_json_one_other_var),
        """--update-env-vars=DRAGONDROP_JOBID=my_id,DRAGONDROP_RESOURCEBLACKLIST='["google_storage_bucket","aws_vpc"]'""",
    )

    case.assertEqual(
        _generate_update_env_vars_string(input_request_json_all_vars),
        """--update-env-vars=DRAGONDROP_JOBID=my_id,DRAGONDROP_ISMODULEMODE=True,DRAGONDROP_RESOURCEWHITELIST='["google_example_resource"]',DRAGONDROP_RESOURCEBLACKLIST='["google_storage_bucket","aws_vpc"]'""",
    )
