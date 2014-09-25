import mock
import pytest

import qitoolchain.database
import qitoolchain.qipackage
import qitoolchain.feed

def test_persistent(toolchain_db):
    foo_package = qitoolchain.qipackage.QiPackage("foo", version="1.3")
    toolchain_db.add_package(foo_package)
    toolchain_db.save()
    db2 = qitoolchain.database.DataBase("bar", toolchain_db.db_path)
    actual_package = db2.packages["foo"]
    assert actual_package == foo_package

def test_adding_same_package_twice(toolchain_db):
    foo_package = qitoolchain.qipackage.QiPackage("foo", version="1.3")
    toolchain_db.add_package(foo_package)
    toolchain_db.add_package(foo_package)
    assert len(toolchain_db.packages) == 1

def test_update(toolchain_db, feed):
    boost_package = qitoolchain.qipackage.QiPackage("boost", version="1.42")
    feed.add_package(boost_package)

    toolchain_db.update(feed.url)
    assert toolchain_db.packages["boost"] == boost_package

    new_boost_package = qitoolchain.qipackage.QiPackage("boost", version="1.44")
    feed.add_package(new_boost_package)
    toolchain_db.update(feed.url)
    assert toolchain_db.packages["boost"] == new_boost_package

def test_downloads_remote_package(toolchain_db, feed):
    boost_package = qitoolchain.qipackage.QiPackage("boost", version="1.42")
    feed.add_package(boost_package, with_path=False, with_url=True)

    toolchain_db.update(feed.url)
    assert toolchain_db.packages["boost"].path

def test_downloads_only_once(toolchain_db, feed):
    boost_package = qitoolchain.qipackage.QiPackage("boost", version="1.42")
    feed.add_package(boost_package, with_path=False, with_url=True)
    with mock.patch.object(toolchain_db, "download_package") as mock_dl:
        toolchain_db.update(feed.url)
        toolchain_db.update(feed.url)
    assert mock_dl.call_count == 1

def test_package_removed_from_feed(toolchain_db, feed):
    boost_package = qitoolchain.qipackage.QiPackage("boost", version="1.42")
    feed.add_package(boost_package)
    toolchain_db.update(feed.url)

    feed.remove_package("boost")
    toolchain_db.update(feed.url)
    assert not toolchain_db.packages

def test_downgrading_package(toolchain_db, feed):
    boost_package = qitoolchain.qipackage.QiPackage("boost", version="1.44")
    feed.add_package(boost_package)

    toolchain_db.update(feed.url)
    assert toolchain_db.packages["boost"] == boost_package

    old_boost_package = qitoolchain.qipackage.QiPackage("boost", version="1.42")
    feed.add_package(old_boost_package)
    toolchain_db.update(feed.url)
    assert toolchain_db.packages["boost"] == old_boost_package

def test_solve_deps(toolchain_db):
    bar_package = qitoolchain.qipackage.QiPackage("bar")
    foo_package = qitoolchain.qipackage.QiPackage("foo")
    foo_package.build_depends = ["bar"]
    toolchain_db.add_package(bar_package)
    toolchain_db.add_package(foo_package)
    res = toolchain_db.solve_deps([foo_package], dep_types=["build"])
    assert res == [bar_package, foo_package]
