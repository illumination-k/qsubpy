from qsubpy.config import Config


class Template:
    def __init__(self, config: Config):
        self.header = []
        self.body = [""]
        self.config = config

    def _make_header(self, mem: str, slot: str):
        self.header.append(self.config.header)
        self.header.append(self.config.resource(mem, slot))

    def _make_body(self):
        self.body.append(self.config.body)

    def make_templates(
        self,
        array_command: str = None,
        mem: str = None,
        slot: str = None,
        common_variables=None,
    ) -> str:
        self._make_header(mem, slot)
        self._make_body()

        if common_variables is not None:
            self.body.append("\n" + self.config.make_common_variables_params())

        if array_command is not None:
            array_header, array_body = self.config.array_header_with_cmd(array_command)
            self.header.append(array_header)
            self.body.append(array_body)

        self.body.append("")

        return self.header + self.body


def make_common_variables_params(common_variables):
    if common_variables is None:
        return ""

    ret = []
    for k, v in common_variables.items():
        ret.append(k + "=" + str(v))
    return "\n".join(ret)


# TODO! implement chunk mode... below is example
"""
#!/bin/bash

arrays=(
    "1 2 3"
    "11 22 33"
    "111 222 333"
)

for array in "${arrays[@]}"; do
    echo "------------"
    data=(${array[@]})
    for a in ${data[@]}; do
        echo ${a}
    done
done
"""
