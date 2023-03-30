"""Unit tests for helper functions within the root blueprint"""
from unittest import TestCase
from src.blueprints.root import _generate_update_env_vars_file


def test_generate_update_env_vars_string():
    """Unit test for the _generate_update_env_vars_string"""
    case = TestCase()

    input_request_json_no_other_vars = {"job_run_id": "my_id"}

    input_request_json_all_vars = {
        "job_run_id": "my_id",
        "resource_white_list": '["google_example_resource"]',
        "resource_black_list": '["google_storage_bucket", "aws_vpc"]',
        "is_module_mode": "true",
    }

    file_flag, output_dict = _generate_update_env_vars_file(
        input_request_json_no_other_vars
    )
    case.assertEqual(file_flag, "--env-vars-file=./env-vars.yml")
    case.assertDictEqual(
        output_dict,
        {"DRAGONDROP_JOBID": "my_id"},
    )

    _, output_dict = _generate_update_env_vars_file(input_request_json_all_vars)
    case.assertDictEqual(
        output_dict,
        {
            "DRAGONDROP_JOBID": "my_id",
            "DRAGONDROP_RESOURCEWHITELIST": '["google_example_resource"]',
            "DRAGONDROP_RESOURCEBLACKLIST": '["google_storage_bucket", "aws_vpc"]',
            "DRAGONDROP_ISMODULEMODE": "true",
        },
    )
