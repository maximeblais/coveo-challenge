from datetime import datetime
from .api.errors import InvalidQuery
import os
import re
import csv


def data_or_none(row, field: str, as_type: type = str, split_on: str = None):
    field_data = row.get(field, '')
    if len(field_data) <= 0:
        return None
    try:
        if split_on:
            field_data = field_data.split(split_on)
            return [(lambda el: as_type(el))(elem) for elem in field_data]
        else:
            return as_type(field_data)
    except Exception as e:
        raise Exception("Error converting data from field {field} to type '{type}'. Reason: {message}"
                        .format(field=field, type=as_type.__name__, message=str(e)))


def fips_to_iso(fips_code: int):
    mapping = {
        1: 'AB', 2: 'BC', 3: 'MB', 4: 'NB', 5: 'NL',
        7: 'NS', 8: 'ON', 9: 'PE', 10: 'QC', 11: 'SK',
        12: 'YT', 13: 'NT', 14: 'NU'
    }
    try:
        return mapping[fips_code]
    except KeyError:
        print("FIPS code {code} has no ISO3166-2 equivalent".format(code=fips_code))
        return None


def match_in_list(items, match_pattern):
    if (not isinstance(items, list)) or len(items) == 0:
        return False

    for item in items:
        if match_pattern.match(item):
            return True

    return False


class GeoRecord:
    def __init__(self, row):
        self.name = data_or_none(row, field='name')
        self.ascii_name = data_or_none(row, field='ascii')
        self.alternate_names = data_or_none(row, field='alt_name', split_on=',')
        self.latitude = data_or_none(row, field='lat', as_type=float)
        self.longitude = data_or_none(row, field='long', as_type=float)
        self.feature_class = data_or_none(row, field='feat_class')
        self.feature_code = data_or_none(row, field='feat_code')
        self.country = data_or_none(row, field='country')
        self.alternate_country_codes = data_or_none(row, field='cc2', split_on=',')
        self.admin1 = fips_to_iso(int(data_or_none(row, field='admin1'))) if self.country == "CA" else data_or_none(row, field='admin1')
        self.admin2 = data_or_none(row, field='admin2')
        self.admin3 = data_or_none(row, field='admin3')
        self.admin4 = data_or_none(row, field='admin4')
        self.population = data_or_none(row, field='population', as_type=int)
        self.elevation = data_or_none(row, field='elevation', as_type=int)
        self.digital_elevation_model = data_or_none(row, field='dem', as_type=int)
        self.timezone = data_or_none(row, field='tz')
        self.modification_date = datetime.strptime(data_or_none(row, field='modified_at'), '%Y-%m-%d').isoformat()\
            if len(row['modified_at']) > 0 else None

    def to_dict(self, simple: bool) -> dict:
        basic = {
            "name": "{name}, {admin1}, {country}".format(name=self.name, admin1=self.admin1, country=self.country),
            "latitude": self.latitude,
            "longitude": self.longitude
        }
        extended = {
            "ascii_name": self.ascii_name,
            "alternate_names": self.alternate_names,
            "feature_class": self.feature_class,
            "feature_code": self.feature_code,
            "country": self.country,
            "alternate_country_codes": self.alternate_country_codes,
            "admin1": self.admin1,
            "admin2": self.admin2,
            "admin3": self.admin3,
            "admin4": self.admin4,
            "population": self.population,
            "elevation": self.elevation,
            "digital_elevation_model": self.digital_elevation_model,
            "timezone": self.timezone,
            "modification_date": self.modification_date
        }
        if simple:
            return basic
        else:
            return {**basic, **extended}


class GeoDB:
    def __init__(self, file_path: str, csv_dialect: str = 'excel-tab'):
        self.geo_points = []

        if not os.path.exists(file_path):
            raise FileNotFoundError("{path} does not exist".format(path=file_path))

        with open(file_path, encoding='utf8') as file:
            reader = csv.DictReader(file, dialect=csv_dialect, quoting=csv.QUOTE_NONE)
            for row in reader:
                try:
                    self.geo_points.append(GeoRecord(row))
                except Exception as e:
                    print(
                        "An error occured while processing geographical point with GeoName ID: {id}. Reason: {message}"
                        .format(id=row['id'], message=str(e)))

    def find_by_name(self, prefix: str):
        prefix = prefix.strip()
        regex_characters = ['*', '.', '[', ']', '\\', '/']
        clean = ''.join(c for c in prefix if c.isalnum() or c not in regex_characters)

        if len(clean) == 0:
            raise InvalidQuery("{prefix} is not a valid search term".format(prefix=prefix))

        try:
            pattern = re.compile(clean, re.IGNORECASE)
        except re.error:
            raise InvalidQuery("{prefix} is not a valid search term".format(prefix=clean))

        candidates = [point for point in self.geo_points if pattern.match(point.name)]
        candidates += [point for point in self.geo_points if pattern.match(point.ascii_name)
                       and point not in candidates]
        #candidates += [point for point in self.geo_points if match_in_list(point.alternate_names, pattern)
        #              and point not in candidates]
        return candidates


db = GeoDB(file_path=os.path.dirname(os.path.abspath(__file__)) + '/data/cities_canada-usa.tsv',
           csv_dialect='excel-tab')
