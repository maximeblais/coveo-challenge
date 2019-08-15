from geosuggest.geodb import GeoRecord, GeoDB, fips_to_iso, data_or_none, match_in_list
from geosuggest.api.errors import InvalidQuery
import re
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


def test_regex_prefix_cleaned(testing_db):
    prefix = ".*Saint-Augustin-de-Desmaures.*"
    assert len(testing_db.find_by_name(prefix)) > 0


def test_regex_prefix_only_wildcard(testing_db):
    prefix = "*"

    with pytest.raises(InvalidQuery):
        testing_db.find_by_name(prefix)


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


def test_match_in_list_matches():
    pattern = re.compile('Al', re.IGNORECASE)
    candidates = ['Beauharnois', 'Victoria', 'Sherbrooke', 'Alma', 'Zanzibar']

    assert match_in_list(candidates, pattern)


def test_match_in_list_no_match():
    pattern = re.compile('Ze', re.IGNORECASE)
    candidates = ['Beauharnois', 'Victoria', 'Sherbrooke', 'Alma', 'Zanzibar']

    assert not match_in_list(candidates, pattern)


def test_match_in_list_with_int_type():
    pattern = re.compile('Te', re.IGNORECASE)
    candidates = 42

    assert not match_in_list(candidates, pattern)


def test_geodb_init_exception_missing_keys():
    from tempfile import mkstemp

    fake_tsv = "name\tascii_name\twhatever\n" \
               "name1\tasciiname1\twhatever1"

    fd, path = mkstemp()
    with open(path, 'w') as f:
        f.write(fake_tsv)
    os.close(fd)

    with pytest.raises(KeyError):
        GeoDB(file_path=path)


def test_georecord_to_dict_simple(testing_db):
    record = testing_db.geo_points[0].to_dict(simple=True)

    assert isinstance(record, dict)
    for field in ['name', 'latitude', 'longitude']:
        assert field in record.keys()


def test_georecord_to_dict_extended(testing_db):
    record = testing_db.geo_points[0].to_dict(simple=False)

    assert isinstance(record, dict)
    for field in ['name', 'latitude', 'longitude', 'ascii_name', 'population']:
        assert field in record.keys()
