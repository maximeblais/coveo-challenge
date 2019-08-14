from geosuggest.geodb import GeoRecord, GeoDB, fips_to_iso, data_or_none
import pytest
import os

@pytest.fixture
def testing_db():
    db = GeoDB(file_path=os.path.dirname(os.path.abspath(__file__)) + '\\test_db_data.tsv',
                 csv_dialect='excel-tab')
    return db


def test_missing_path():
    file_path = "/some/missing/file.tsv"
    with pytest.raises(FileNotFoundError):
        GeoDB(file_path)


def test_missing_record(testing_db):
    assert len(testing_db.find_by_name('sdjhrotkdigkdlgppweqwbqwgegqwe')) == 0


def test_spaces_and_newlines_start_end_prefix(testing_db):
    prefix = "       \t\n \r\n      Cutler \n \t"
    assert len(testing_db.find_by_name(prefix)) > 0


def test_valid_prefix_with_spaces_middle(testing_db):
    prefix = "Truth or Consequences"
    assert len(testing_db.find_by_name(prefix)) > 0


def test_fips_to_iso():
    assert fips_to_iso(99) is None
    assert fips_to_iso(int('01')) == 'AB'


def test_data_or_none_missing_field():
    row = {
        'fieldA': 'valueA'
    }
    assert data_or_none(row=row, field='fieldB') is None


def test_data_or_none_invalid_conversion():
    row = {
        'fieldA': 'valueA'
    }
    with pytest.raises(Exception):
        data_or_none(row=row, field='fieldA', as_type=int)


def test_data_or_none_existing_field():
    row = {
        'fieldA': 'valueA'
    }
    assert data_or_none(row=row, field='fieldA') == 'valueA'
