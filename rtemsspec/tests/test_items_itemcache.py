# SPDX-License-Identifier: BSD-2-Clause
""" Unit tests for the rtemsspec.items module. """

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
import pytest

from rtemsspec.items import EmptyItem, ItemCache, ItemMapper, ItemTemplate
from rtemsspec.tests.util import create_item_cache_config_and_copy_spec


def test_config_error():
    with pytest.raises(KeyError):
        ItemCache({})


def test_load(tmpdir):
    config = create_item_cache_config_and_copy_spec(tmpdir, "spec-item-cache")
    item_cache = ItemCache(config)
    assert item_cache.updates
    cache_dir = config["cache-directory"]
    assert os.path.exists(os.path.join(cache_dir, "spec", "spec.pickle"))
    assert os.path.exists(os.path.join(cache_dir, "spec", "d", "spec.pickle"))
    assert item_cache["/d/c"]["v"] == "c"
    assert item_cache["/p"]["v"] == "p"
    p = item_cache["/p"]
    assert p["v"] == "p"
    assert p.map("/p") == p
    assert p.map("p") == p
    a = item_cache.all
    assert len(a) == 2
    assert a["/p"]["v"] == "p"
    assert a["/d/c"]["v"] == "c"
    item_cache_2 = ItemCache(config)
    assert not item_cache_2.updates
    assert item_cache_2["/d/c"]["v"] == "c"
    with open(os.path.join(tmpdir, "spec", "d", "c.yml"), "w+") as out:
        out.write("links:\n- role: null\n  uid: ../p\nv: x\n")
    item_cache_3 = ItemCache(config)
    assert item_cache_3.updates
    assert item_cache_3["/d/c"]["v"] == "x"
    item = item_cache_3.add_volatile_item(
        os.path.join(os.path.dirname(__file__), "spec/root.yml"), "/foo/bar")
    assert item.uid == "/foo/bar"
    assert item.type == ""
    assert item["type"] == "spec"
    os.remove(os.path.join(tmpdir, "spec", "d", "c.yml"))
    item_cache_4 = ItemCache(config)
    assert item_cache_4.updates
    with pytest.raises(KeyError):
        item_cache_4["/d/c"]


def test_load_link_error(tmpdir):
    config = create_item_cache_config_and_copy_spec(tmpdir,
                                                    "spec-item-cache-2")
    with pytest.raises(
            KeyError,
            match=r"^\"item '/a' links to non-existing item 'nix'\"$"):
        ItemCache(config)


def test_load_yaml_error(tmpdir):
    config = create_item_cache_config_and_copy_spec(tmpdir,
                                                    "spec-item-cache-3")
    match = r"""YAML error while loading specification item file '.*invalid.yml': while parsing a block mapping
expected <block end>, but found ':'
  in "<unicode string>", line 1, column 1:
    :
    \^"""
    with pytest.raises(IOError, match=match):
        ItemCache(config)


def get_x_to_b_value(ctx):
    assert ctx.key == "x-to-b"
    return ctx.value["b"]


class Mapper(ItemMapper):
    def __init__(self, item):
        super().__init__(item)

    def u(self, value):
        return "u" + value

    def v(self, value):
        return "v" + value

    def dup(self, value):
        return value + value


def test_item_mapper(tmpdir):
    config = create_item_cache_config_and_copy_spec(tmpdir, "spec-item-cache")
    item_cache = ItemCache(config)
    item = item_cache["/p"]
    base_mapper = ItemMapper(item)
    assert base_mapper["d/c:v"] == "c"
    mapper = Mapper(item)
    assert mapper.substitute(None) == ""
    assert mapper.substitute_with_prefix(None, "v") == ""
    with mapper.prefix("v"):
        assert mapper[".:."] == "p"
        assert mapper[".:../x/y"] == "z"
        item_2, key_path_2, value_2 = mapper.map(".:.")
        assert item_2 == item
        assert key_path_2 == "/v"
        assert value_2 == "p"
        assert mapper.substitute("$$${.:.}") == "$p"
    assert mapper.substitute_with_prefix("$$${.:.}", "v") == "$p"
    with mapper.prefix("x"):
        with mapper.prefix("y"):
            assert mapper[".:."] == "z"
    assert mapper["."] == "/p"
    assert mapper["d/c"] == "/d/c"
    assert mapper["d/c:v"] == "c"
    assert mapper["d/c:a/b"] == "e"
    assert mapper["d/c:a/b|u"] == "ue"
    mapper.add_get_value(":/a/x-to-b", get_x_to_b_value)
    assert mapper["d/c:a/x-to-b|u|v"] == "vue"
    assert mapper["d/c:a/f[1]"] == 2
    assert mapper["d/c:a/../a/f[3]/g[0]|dup"] == 8
    item_3, key_path_3, value_3 = mapper.map("/p:/v")
    assert item_3 == item
    assert key_path_3 == "/v"
    assert value_3 == "p"
    with pytest.raises(StopIteration):
        for something in mapper:
            pass
    with pytest.raises(AttributeError):
        len(mapper)
    recursive_mapper = ItemMapper(item, recursive=True)
    assert recursive_mapper.substitute("${.:/r1/r2/r3}") == "foobar"


def test_empty_item_mapper():
    item = EmptyItem()
    mapper = ItemMapper(item)
    assert mapper.item == item
    item_2 = EmptyItem()
    mapper.item = item_2
    assert mapper.item == item_2
