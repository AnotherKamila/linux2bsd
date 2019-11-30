from linux2bsd import translate

def test_translate():
    assert translate('apt', to='bsd'  )[0][2] == 'pkg'
    assert [x[2] for x in translate('pkg', to='linux')] == ['apt', 'rpm', 'yum']
