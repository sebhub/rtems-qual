# SPDX-License-Identifier: BSD-2-Clause
""" Unit tests for the rtemsqual.build module. """

# Copyright (C) 2020 embedded brains GmbH (http://www.embedded-brains.de)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os
import shutil

from rtemsqual.build import gather_files
from rtemsqual.items import ItemCache


def test_build(tmpdir):
    item_cache_config = {}
    item_cache_config["cache-directory"] = "cache"
    spec_src = os.path.join(os.path.dirname(__file__), "spec-build")
    spec_dst = os.path.join(tmpdir, "spec")
    shutil.copytree(spec_src, spec_dst)
    item_cache_config["paths"] = [os.path.normpath(spec_dst)]
    ic = ItemCache(item_cache_config)

    build_config = {}
    build_config["arch"] = "foo"
    build_config["bsp"] = "bar"
    build_config["enabled"] = ["A"]
    build_config["sources"] = ["a", "b"]
    build_config["uids"] = ["g"]
    files = gather_files(build_config, ic)
    assert files == ["a", "b", "stu", "jkl", "mno", "abc", "def"]
