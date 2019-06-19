import itertools
import operator
import pickle
import os.path
# noinspection PyPackageRequirements
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
# noinspection PyPackageRequirements
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '12shYYOLyU4PpdEyw5-ObvLhgRP6aggUgrIfpGA-BWIE'
PHYS_RANGE = 'A2:B'
SAMPLE_SHEET_NAMES = 'Голова Тело Руки Ноги'.split()
RANGES = ['{}!{}'.format(sheet, PHYS_RANGE) for sheet in SAMPLE_SHEET_NAMES]


def main():
    sheet = _get_sheet()

    ranges_values = list(
        sheet.get(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=_range
        ).execute().get('values', []) for _range in RANGES
    )
    print(ranges_values)


def _combo_gen(ranges_values):
    """
    >>> list(
    ... _combo_gen([[1,2], [3,4], [5,6,7]]))  # doctest: +NORMALIZE_WHITESPACE
    [[1, 3, 5], [1, 3, 6], [1, 3, 7], [1, 4, 5], [1, 4, 6], [1, 4, 7],
    [2, 3, 5], [2, 3, 6], [2, 3, 7], [2, 4, 5], [2, 4, 6], [2, 4, 7]]
    """
    ranges_count = len(ranges_values)
    ranges_lens = list(map(len, ranges_values))
    cursors = [0 for _ in ranges_values]

    while True:
        positions_to_ranges = zip(cursors, ranges_values)
        combo = [
            position_to_range[1][position_to_range[0]]
            for position_to_range in positions_to_ranges
        ]
        yield combo

        top_range = -ranges_count - 1
        for range_number, rightmost_cursor in zip(
                range(-1, top_range, -1), cursors[::-1]
        ):
            rightmost_cursor += 1
            range_len = ranges_lens[range_number]

            if rightmost_cursor < range_len:
                cursors[range_number] += 1
                break
            else:
                if range_number == top_range + 1:
                    return
                cursors[range_number] = 0


def _get_sheet():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    return sheet.values()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
