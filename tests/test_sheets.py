from storage.sheets_store import SheetsStore


class FakeSheet:
    def __init__(self):
        self.rows=[['event_id','part','total','kind','payload']]
        self.fail_after_write=False
    def get_all_values(self): return self.rows
    def append_rows(self,rows,value_input_option):
        assert value_input_option=='RAW'
        self.rows.extend(rows)
        if self.fail_after_write:
            self.fail_after_write=False
            raise TimeoutError('Response lost after successful write')


def test_chunking_and_retry_after_unknown_write():
    store=SheetsStore.__new__(SheetsStore); store.sheet=FakeSheet()
    e={'id':'stable','kind':'correction','data':{'text':'=SUM(A1:A2)'+('tiếng Việt 🙂'*6000)}}
    store.sheet.fail_after_write=True
    try: store.save(e)
    except TimeoutError: pass
    count=len(store.sheet.rows)
    store.save(e)
    assert len(store.sheet.rows)==count
    assert store.load()==[e]
    assert all(len(r[4])<=12000 for r in store.sheet.rows[1:])


def test_partial_record_repaired_without_duplicate_parts():
    store=SheetsStore.__new__(SheetsStore); store.sheet=FakeSheet()
    e={'id':'stable','kind':'correction','data':{'text':'x'*40000}}
    store.save(e)
    store.sheet.rows.pop(2)
    assert store.load()==[]
    store.save(e)
    assert store.load()==[e]
