from pandas import read_csv, read_excel
import apps.core.files.models as models_files
import apps.core.files.exceptions as exc_files


def get_sheet_headers(stored_file_path: models_files.StoredFilePath, csv_delimiter=None):
    df = None
    if stored_file_path.extension in ['.xls', '.xlsx', '.xlsm', '.xlsb', '.odf', '.ods', '.odt']:
        df = read_excel(stored_file_path.path, sheet_name=0)
    elif stored_file_path.extension == '.csv':
        df = read_csv(stored_file_path.path, sep=csv_delimiter)
    else:
        raise exc_files.FileParsingException('Failed to recognize file extension. Could not retrieve sheet headers')

    cols = []

    for col in df.columns:
        cols.append(col)

    return cols
