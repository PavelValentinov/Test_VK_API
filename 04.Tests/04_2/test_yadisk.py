import pytest

from YaDisk import YaUploader


def test_create_and_remove_test_folder():
    ya = YaUploader()
    assert ya.get_status_code() == 404
    assert ya.create_folder() == (201, 'https://cloud-api.yandex.net/v1/disk/resources?path=disk%3A%2Ftest_folder')
    assert ya.get_status_code() == 200
    assert ya.remove_folder() == 204


def test_create_and_remove_another_folder():
    ya = YaUploader('another_folder')
    assert ya.get_status_code() == 404
    assert ya.create_folder() == (201, 'https://cloud-api.yandex.net/v1/disk/resources?path=disk%3A%2Fanother_folder')
    assert ya.get_status_code() == 200
    assert ya.remove_folder() == 204


if __name__ == '__main__':
    pytest.main()
