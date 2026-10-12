"""Single learner append log. RAW cells; chunked JSON, deterministic event IDs."""
import json
import gspread
from gspread.exceptions import WorksheetNotFound


class SheetsStore:
    def __init__(self, credentials, spreadsheet_id):
        client = gspread.service_account_from_dict(dict(credentials))
        client.set_timeout(20)
        book = client.open_by_key(spreadsheet_id)
        try:
            self.sheet = book.worksheet('Events')
        except WorksheetNotFound:
            self.sheet = book.add_worksheet('Events',rows=1000,cols=5)
            self.sheet.append_row(['event_id','part','total','kind','payload'],value_input_option='RAW')

    def _groups(self):
        groups = {}
        for row in self.sheet.get_all_values()[1:]:
            if len(row) >= 5:
                groups.setdefault(row[0],{})[int(row[1])] = (int(row[2]),row[4])
        return groups

    def load(self):
        events = []
        for parts in self._groups().values():
            count = next(iter(parts.values()))[0]
            if set(parts) == set(range(count)):
                events.append(json.loads(''.join(parts[i][1] for i in range(count))))
        return events

    def save(self,event):
        payload = json.dumps(event,ensure_ascii=False)
        # Split by UTF-16 units conservatively: 12k Unicode chars <=24k units.
        chunks = [payload[i:i+12000] for i in range(0,len(payload),12000)]
        present = self._groups().get(event['id'],{})
        for part,(total,value) in present.items():
            if total != len(chunks) or part >= len(chunks) or chunks[part] != value:
                raise ValueError('Xung đột ID trên Sheets')
        rows = [[event['id'],str(i),str(len(chunks)),event['kind'],chunk] for i,chunk in enumerate(chunks) if i not in present]
        if rows:
            self.sheet.append_rows(rows,value_input_option='RAW')
        confirmed = self._groups().get(event['id'],{})
        if len(confirmed) != len(chunks) or any(confirmed[i][1] != text for i,text in enumerate(chunks)):
            raise IOError('Sheets chưa xác nhận đủ nội dung')
