"""Unit tests for helper functions within the root blueprint"""
from unittest import TestCase
from src.blueprints.root import _generate_update_env_vars_file


def test_generate_update_env_vars_string():
    """Unit test for the _generate_update_env_vars_string"""
    case = TestCase()

    input_request_json_all_vars = {
        "CLOUDCONCIERGE_JOBID": "my_id",
        "CLOUDCONCIERGE_RESOURCESWHITELIST": '["google_example_resource"]',
        "CLOUDCONCIERGE_RESOURCESBLACKLIST": '["google_storage_bucket", "aws_vpc"]',
        "CLOUDCONCIERGE_ISMODULEMODE": "true",
    }

    file_flag, output_dict = _generate_update_env_vars_file(input_request_json_all_vars)
    case.assertEqual(file_flag, "--env-vars-file=./env-vars.yml")
    case.assertDictEqual(
        output_dict,
        {
            "CLOUDCONCIERGE_JOBID": "my_id",
            "CLOUDCONCIERGE_RESOURCESWHITELIST": '["google_example_resource"]',
            "CLOUDCONCIERGE_RESOURCESBLACKLIST": '["google_storage_bucket", "aws_vpc"]',
            "CLOUDCONCIERGE_ISMODULEMODE": "true",
        },
    )
