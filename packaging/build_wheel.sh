#!/bin/bash
set -ex

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. "$script_dir/pkg_helpers.bash"

export BUILD_TYPE=wheel
setup_env 0.6.0
setup_wheel_python
pip_install numpy pyyaml future ninja
# TODO remove after https://github.com/pytorch/pytorch/pull/27282 gets merged
pip_install six
setup_pip_pytorch_version
python setup.py clean
IS_WHEEL=1 python setup.py bdist_wheel
