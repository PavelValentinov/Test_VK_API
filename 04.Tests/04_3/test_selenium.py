import pytest

from ya_passport_auth import YaAuth

true_user = ''
true_pass = ''
false_user = 'AaBbCcVv'
false_pass = 'AaBbCcVv'


@pytest.mark.skipif((true_user == '' or true_pass == ''), reason='requires true data')
def test_true_data():
    auth = YaAuth(true_user, true_pass)
    assert 'welcome' in auth.input_login()
    assert 'profile' in auth.input_pass()
    assert 'CLOSED' == auth.close()


@pytest.mark.skipif(true_pass == '', reason='requires true data')
def test_false_username():
    auth = YaAuth(false_user, true_pass)
    assert 'welcome' in auth.input_login()
    assert 'profile' not in auth.input_pass()
    assert 'CLOSED' == auth.close()


@pytest.mark.skipif(true_user == '', reason='requires true data')
def test_false_password():
    auth = YaAuth(true_user, false_pass)
    assert 'welcome' in auth.input_login()
    assert 'profile' not in auth.input_pass()
    assert 'CLOSED' == auth.close()


def test_false_data():
    auth = YaAuth(false_user, false_pass)
    assert 'welcome' in auth.input_login()
    assert 'profile' not in auth.input_pass()
    assert 'CLOSED' == auth.close()


if __name__ == '__main__':
    pytest.main()
    YaAuth.close()
