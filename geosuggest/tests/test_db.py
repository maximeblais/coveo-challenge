from geosuggest.geodb import GeoRecord, GeoDB, fips_to_iso, data_or_none, match_in_list
from geosuggest.api.errors import InvalidQuery
import re
import pytest
import os

# Simple fixture for a lite test database, containing a subset of our real data
@pytest.fixture
def testing_db():
    db = GeoDB(file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_db_data.tsv'),
               csv_dialect='excel-tab')
    return db


# Verify that we raise an exception when trying to instantiate a GeoDB with a missing file
def test_missing_path():
    file_path = "/some/missing/file.tsv"
    with pytest.raises(FileNotFoundError):
        GeoDB(file_path)


# Verify that we return an empty list when there are no candidates for a given prefix
def test_missing_record(testing_db):
    assert len(testing_db.find_by_name('sdjhrotkdigkdlgppweqwbqwgegqwe')) == 0


# Verify that prefix is properly cleaned of any whitespace characters (at start and end)
def test_spaces_and_newlines_start_end_prefix(testing_db):
    prefix = "       \t\n \r\n      Cutler \n \t"
    assert len(testing_db.find_by_name(prefix)) > 0


# Verify that whitespace in the middle of the prefix is kept
def test_valid_prefix_with_spaces_middle(testing_db):
    prefix = "Truth or Consequences"
    assert len(testing_db.find_by_name(prefix)) > 0


# Verify that regex characters are properly removed from the prefix
def test_regex_prefix_cleaned(testing_db):
    prefix = ".*Saint-Augustin-de-Desmaures.*"
    assert len(testing_db.find_by_name(prefix)) > 0


# Verify that a single wildcard prefix raises an InvalidQuery, as its cleaned and such becomes an empty string
def test_regex_prefix_only_wildcard(testing_db):
    prefix = "*"

    with pytest.raises(InvalidQuery):
        testing_db.find_by_name(prefix)


# Verify our fips_to_iso function
def test_fips_to_iso():
    assert fips_to_iso(99) is None
    assert fips_to_iso(int('01')) == 'AB'


# Verify that data_or_none returns None if a field is missing
def test_data_or_none_missing_field():
    row = {
        'fieldA': 'valueA'
    }
    assert data_or_none(row=row, field='fieldB') is None


# Verify that we raise an exception when trying to perform an invalid conversion
def test_data_or_none_invalid_conversion():
    row = {
        'fieldA': 'valueA'
    }
    with pytest.raises(Exception):
        data_or_none(row=row, field='fieldA', as_type=int)


# Verify that data_or_none properly returns data
def test_data_or_none_existing_field():
    row = {
        'fieldA': 'valueA'
    }
    assert data_or_none(row=row, field='fieldA') == 'valueA'


# Verify our match_in_list function, with a match
def test_match_in_list_matches():
    pattern = re.compile('Al', re.IGNORECASE)
    candidates = ['Beauharnois', 'Victoria', 'Sherbrooke', 'Alma', 'Zanzibar']

    assert match_in_list(candidates, pattern)


# Verify our match_in_list function, with no match
def test_match_in_list_no_match():
    pattern = re.compile('Ze', re.IGNORECASE)
    candidates = ['Beauharnois', 'Victoria', 'Sherbrooke', 'Alma', 'Zanzibar']

    assert not match_in_list(candidates, pattern)


# Verify our match_in_list function, when trying to match a string pattern on an invalid type, that it returns False
def test_match_in_list_with_int_type():
    pattern = re.compile('Te', re.IGNORECASE)
    candidates = 42

    assert not match_in_list(candidates, pattern)


# Verify that we raise an exception when the TSV format is not what we expect
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


# Test the GeoRecord conversion to a 'simple' dictionary
def test_georecord_to_dict_simple(testing_db):
    record = testing_db.geo_points[0].to_dict(simple=True)

    assert isinstance(record, dict)
    for field in ['name', 'latitude', 'longitude']:
        assert field in record.keys()


# Test the GeoRecord conversion to an 'extended' dictionary
def test_georecord_to_dict_extended(testing_db):
    record = testing_db.geo_points[0].to_dict(simple=False)

    assert isinstance(record, dict)
    for field in ['name', 'latitude', 'longitude', 'ascii_name', 'population']:
        assert field in record.keys()
