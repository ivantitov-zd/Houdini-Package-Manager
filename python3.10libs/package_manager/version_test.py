from package_manager.version import Version
from package_manager.version import VersionPattern
from package_manager.version import VersionRange


def test_basic_scenarios():
    assert Version('2.7') < '3.3'
    assert Version('3.3.0') == '3.3'
    assert Version('6') < Version('10')
    assert '10.2.305' in VersionRange.from_pattern('6-10.3')
    assert '18.5' in VersionPattern('18+')
    assert '17' not in VersionPattern('18+')
    assert Version('0.3-beta') == Version('0.3.0-beta')
    assert Version('0.4-beta') > Version('0.4-alpha')
    assert Version('0.4-beta.alpha') < Version('0.4-alpha')
