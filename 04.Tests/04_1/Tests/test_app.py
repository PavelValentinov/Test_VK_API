import os
from unittest.mock import patch

import pytest

from src import app

new_doc_fixture = ['1234567890', 'licence', 'Smirnoff', '1']
move_fixture = ['10006', '3']
del_fixture = ['11-2', '10005']
doc_num = '10006'
shelf_num = '2'
user_commands = ['ap', 'p', 'l', 's', 'a', 'd', 'm', 'as', 'q', 'help']


@pytest.fixture()
def setup():
    app.directories, app.documents = app.update_date()


def test_files_exist():
    path = str(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../src', 'fixtures'))
    assert os.path.exists(path) is True
    assert os.path.exists(os.path.join(path, 'directories.json')) is True
    assert os.path.exists(os.path.join(path, 'documents.json')) is True


def test_update_date():
    expected_func_return = tuple
    expected_directories = dict
    expected_documents = list
    update_date = app.update_date()

    assert type(update_date) == expected_func_return
    assert type(app.directories) == expected_directories
    assert type(update_date[0]) == expected_directories
    assert type(app.documents) == expected_documents
    assert type(update_date[1]) == expected_documents
    assert app.directories != app.documents


@patch('builtins.input', side_effect=new_doc_fixture)
def test_add_new_doc(mock_input):
    app.add_new_doc()
    doc_number, doc_type, doc_owner, shelf = new_doc_fixture
    new_doc = {'type': doc_type, 'number': doc_number, 'name': doc_owner}
    assert new_doc in app.documents
    assert shelf in app.directories


def test_show_all_docs_info():
    all_docs = [f'{doc["type"]} "{doc["number"]}" "{doc["name"]}"' for doc in app.documents]
    result = app.show_all_docs_info()
    assert result == all_docs


def test_show_document_info():
    for doc in app.documents:
        result = f'{doc["type"]} "{doc["number"]}" "{doc["name"]}"'
        assert app.show_document_info(doc) == result


@patch('builtins.input', side_effect=move_fixture)
def test_move_doc_to_shelf(mock_input, capfd):
    app.move_doc_to_shelf()
    user_doc_number, user_shelf_number = move_fixture
    out, err = capfd.readouterr()
    assert out == f'Документ номер "{user_doc_number}" был перемещен на полку номер "{user_shelf_number}"\n'


@pytest.mark.parametrize("test_input,expected", [("2207 876234", True), ('111', False)])
def test_remove_doc_from_shelf(test_input, expected, setup):
    assert app.remove_doc_from_shelf(test_input) == expected


def test_append_doc_to_shelf():
    app.append_doc_to_shelf(new_doc_fixture[0], '1')
    assert new_doc_fixture[0] in app.directories['1']


@patch('builtins.input', return_value=del_fixture)
def test_delete_doc(mock_input):
    for input_ in mock_input:
        result = app.delete_doc()
        if input_ == mock_input[0]:
            assert (input_, True) == result
        else:
            assert (input_, False) == result


@patch('builtins.input', return_value=doc_num)
def test_get_doc_shelf(mock_input):
    assert '2' == app.get_doc_shelf()


@pytest.mark.parametrize('test_input, expected', [('1', ('1', False)), ('5', ('5', True))])
def test_add_new_shelf(test_input, expected):
    assert app.add_new_shelf(test_input) == expected


def test_get_all_doc_owners_names():
    owners = {doc['name'] for doc in app.documents}
    assert owners == app.get_all_doc_owners_names()


@patch('builtins.input', return_value=doc_num)
def test_get_doc_owner_name(mock_input):
    assert app.get_doc_owner_name() == "Аристарх Павлов"


if __name__ == '__main__':
    pytest.main()
