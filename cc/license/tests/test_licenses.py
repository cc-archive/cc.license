import nose.tools

def test_find_sampling_selector():
    from zope.interface import implementedBy
    import cc.license

    sampling_selector = cc.license.get_selector('recombo')()
    return sampling_selector

def test_find_sampling_licenses():
    selector = test_find_sampling_selector()
    lic = selector.by_code('sampling')
    assert not lic.libre
    assert lic.deprecated
    lic = selector.by_code('sampling+')
    assert not lic.deprecated

def test_find_pd():
    from zope.interface import implementedBy
    import cc.license

    pd_selector = cc.license.get_selector('publicdomain')()
    pd = pd_selector.by_code('publicdomain')
    return pd

def test_pd():
    pd = test_find_pd()
    assert pd.libre
    assert pd.jurisdiction == 'Your mom'
    assert not pd.deprecated
    assert pd.jurisdiction == 'Your mom'
    assert pd.license_code == 'publicdomain'
    assert pd.name() == 'Public Domain' == pd.name('en')
    assert pd.name('hr') == u'Javna domena'
