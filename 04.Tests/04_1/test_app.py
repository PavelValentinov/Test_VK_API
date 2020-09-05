import os

import pytest

from src import app


@pytest.fixture()
def update_date():
    return app.update_date()


# @pytest.fixture()
# def add_new_doc():
#     return app.add_new_doc()
#
#
# @pytest.fixture()
# def secretary_program_start():
#     return app.secretary_program_start()
#
#
# @pytest.fixture()
# def get_all_doc_owners_names():
#     return app.get_all_doc_owners_names()
#
#
# @pytest.fixture()
# def get_doc_owner_name():
#     return app.get_doc_owner_name()
#
#
# @pytest.fixture()
# def delete_doc():
#     return app.get_doc_owner_name()
#
#
# @pytest.fixture()
# def get_doc_shelf():
#     return app.get_doc_shelf()
#
#
# @pytest.fixture()
# def move_doc_to_shelf():
#     return app.move_doc_to_shelf()
#
#
# @pytest.fixture()
# def show_all_docs_info():
#     return app.show_all_docs_info()
#
#
# @pytest.fixture()
# def add_new_shelf(shelf_number=''):
#     pass
#
#
# @pytest.fixture()
# def check_document_existance(user_doc_number):
#     pass
#
#
# @pytest.fixture()
# def remove_doc_from_shelf(doc_number):
#     pass
#
#
# @pytest.fixture()
# def append_doc_to_shelf(doc_number, shelf_number):
#     pass
#
#
# @pytest.fixture()
# def show_document_info(document):
#     pass


def test_files_exist():
    path = str(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
    assert os.path.exists(path) is True
    assert os.path.exists(os.path.join(path, 'fixtures/directories.json')) is True
    assert os.path.exists(os.path.join(path, 'fixtures/documents.json')) is True


def test_update_date(update_date):
    expected_func_return = tuple
    expected_directories = dict
    expected_documents = list
    directories, documents = app.update_date()
    assert type(update_date) == expected_func_return
    assert (directories, documents) == (update_date[0], update_date[1])
    assert type(directories) == expected_directories
    assert type(update_date[0]) == expected_directories
    assert update_date[0] == directories
    assert type(documents) == expected_documents
    assert type(update_date[1]) == expected_documents
    assert update_date[1] == documents
    assert directories != documents

@pytest.mark.skip
def test_show_all_docs_info(show_all_docs_info):
    pass


if __name__ == '__main__':
    pytest.main()
