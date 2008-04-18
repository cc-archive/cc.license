import nose.tools

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
