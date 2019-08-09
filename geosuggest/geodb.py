from datetime import datetime
import csv


class GeoRecord:
    def __init__(self, row):
        def data_or_none(field: str, as_type: type = str, split_on: str = None) -> object:
            field_data = row.get(field, '')
            if len(field_data) <= 0:
                return None
            try:
                if split_on:
                    field_data = field_data.split(split_on)
                    return [(lambda el: as_type(el))(elem) for elem in field_data]
                else:
                    return as_type(field_data)
            except ValueError as e:
                print("Error converting data from field {field} to type '{type}'. Reason: {message}"
                      .format(field=field, type=as_type.__name__, message=str(e)))

        self.name = data_or_none('name')
        self.ascii_name = data_or_none('ascii')
        self.alternate_names = data_or_none('alt_name', split_on=',')
        self.latitude = data_or_none('lat', as_type=float)
        self.longitude = data_or_none('long', as_type=float)
        self.feature_class = data_or_none('feat_class')
        self.feature_code = data_or_none('feat_code')
        self.country = data_or_none('country')
        self.alternate_country_codes = data_or_none('cc2', split_on=',')
        self.admin1 = data_or_none('admin1')
        self.admin2 = data_or_none('admin2')
        self.admin3 = data_or_none('admin3')
        self.admin4 = data_or_none('admin4')
        self.population = data_or_none('population', as_type=int)
        self.elevation = data_or_none('elevation', as_type=int)
        self.digital_elevation_model = data_or_none('dem', as_type=int)
        self.timezone = data_or_none('tz')
        self.modification_date = datetime.strptime(data_or_none('modified_at'), '%Y-%m-%d') if len(row['modified_at']) > 0 else None


class GeoDB:
    def __init__(self, file_path, csv_dialect='excel-tab'):
        self.geo_points = {}
        with open(file_path, encoding='utf8') as file:
            reader = csv.DictReader(file, dialect=csv_dialect, quoting=csv.QUOTE_NONE)
            for row in reader:
                try:
                    self.geo_points[row['id']] = GeoRecord(row)
                except Exception as e:
                    print(
                        "An error occured while processing geographical point with GeoName ID: {id}. Reason: {message}"
                        .format(id=row['id'], message=str(e)))
