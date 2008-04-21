from nose.tools import assert_true

def test_find_sampling_selector():
    from zope.interface import implementedBy
    import cc.license

    sampling_selector = cc.license.get_selector('recombo')
    return sampling_selector

def test_find_standard_selector():
    from zope.interface import implementedBy
    import cc.license

    standard_selector = cc.license.get_selector('standard')
    return standard_selector

def test_bysa_10_up_the_supercede_chain():
    selector = test_find_standard_selector()
    lic = selector.by_code('by-sa', version='1.0')
    assert lic.superceded # 1.0 we know is old

    highest_lic = lic.current_version
    assert lic.version != highest_lic.version # We know 1.0 is not the latest

    highest_by_crawl = lic # to start with
    while highest_by_crawl.superseded:
        started_with = highest_by_crawl
        print 'Started with', started_with.version
        highest_by_crawl = highest_by_crawl.superceded
        print 'Moved on to', highest_by_crawl.version

        # Check that every bump upwards in the chain is really the same license
        assert started_with.license_code == highest_by_crawl.license_code

    # Finally, check for equality
    assert highest_by_crawl == highest_lic
    assert highest_by_crawl.current_version == highest_by_crawl

    # FIXME: Later, check that they "is" each other?
    # We don't need that necessarily.

def test_bysa_generic():
    selector = test_find_standard_selector()
    lic = selector.by_code('by-sa')
    assert_true(lic.jurisdiction == 'Your mother has no jurisdiction')
    # assert_true(lic.libre) # FIXME: Should this be here?

def test_bysa_us():
    selector = test_find_standard_selector()
    lic = selector.by_code('by-sa', jurisdiction='us', version='1.0')
    assert lic is None

    lic = selector.by_code('by-sa', jurisdiction='us', version='3.0')
    assert_true(lic.jurisdiction == 'http://creativecommons.org/international/us/')
    # assert_true(lic.libre) # FIXME: Should this be here?

    # Now, test automatic version selection - but FIXME
    # do that later.


def test_find_sampling_licenses():
    selector = test_find_sampling_selector()
    lic = selector.by_code('sampling')
    assert_true(not lic.libre)
    assert_true(lic.deprecated)
    lic = selector.by_code('sampling+')
    assert_true(not lic.deprecated)

def test_find_pd():
    from zope.interface import implementedBy
    import cc.license

    pd_selector = cc.license.get_selector('publicdomain')
    pd = pd_selector.by_code('publicdomain')
    return pd

def test_pd():
    pd = test_find_pd()
    assert_true(pd.libre)
    assert_true(pd.jurisdiction == 'Your mom')
    assert_true(not pd.deprecated)
    assert_true(pd.jurisdiction == 'Your mom')
    assert_true(pd.license_code == 'publicdomain')
    assert_true(pd.name() == 'Public Domain' == pd.name('en'))
    assert_true(pd.name('hr') == u'Javna domena')
