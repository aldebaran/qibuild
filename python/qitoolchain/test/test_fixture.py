import qitoolchain.database
import qitoolchain.feed
import qitoolchain.qipackage

def test_feed(feed):
    boost_package = qitoolchain.qipackage.QiPackage("boost", "1.42")
    boost_package.url = "ftp://example.org/boost-1.42.zip"
    feed.add_package(boost_package)
    parser = qitoolchain.feed.ToolchainFeedParser()
    parser.parse(feed.url)
    packages = parser.get_packages()
    assert packages[0].url == boost_package.url
