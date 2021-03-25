from qsubpy.config import Config, read_config


def test_config_resource():
    config = read_config("config.toml")
    expected_default_resource = "#$ -l s_veme=4G -l mem_req=4G\n#$ -pe def_slot 1"
    expected_custom_resource = "#$ -l s_veme=16G -l mem_req=16G\n#$ -pe def_slot 4"
    assert config.resource() == expected_default_resource
    assert config.resource("16G", "4") == expected_custom_resource

def test_array_job():
    config = read_config("config.toml")

    array_header, array_body = config.array_header_with_cmd("echo 'a b'")
    assert array_header == "#$ -t 1-2:1"
    assert array_body == "array=($(echo 'a b'))\nelem=${array[$(($SEG_TASK_ID-1))]}"
    