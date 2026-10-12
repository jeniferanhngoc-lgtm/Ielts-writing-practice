"""Append-only events. SQLite for personal local use; demo has no durable writes."""
import json
import sqlite3
from pathlib import Path


class LocalStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connection() as db:
            db.execute('CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, payload TEXT NOT NULL)')

    def connection(self):
        return sqlite3.connect(self.path)

    def load(self):
        with self.connection() as db:
            return [json.loads(r[0]) for r in db.execute('SELECT payload FROM events ORDER BY rowid')]

    def save(self,event):
        payload = json.dumps(event,ensure_ascii=False)
        with self.connection() as db:
            old = db.execute('SELECT payload FROM events WHERE id=?',(event['id'],)).fetchone()
            if old and json.loads(old[0]) != event:
                raise ValueError('ID đã tồn tại với nội dung khác')
            db.execute('INSERT OR IGNORE INTO events VALUES (?,?)',(event['id'],payload))


def merge_events(existing, incoming):
    merged = {e['id']:e for e in existing}
    for event in incoming:
        if not isinstance(event,dict) or not all(k in event for k in ['id','kind','data']):
            raise ValueError('Bản ghi tiến độ không hợp lệ')
        if event['kind'] not in ['attempt','correction','session','settings','self_review']:
            raise ValueError('Loại bản ghi không hợp lệ')
        if event['kind'] == 'attempt':
            required = ['attempt_id','exercise_id','task_id','answer','grading_type','submitted_at','score','max_score']
            if not all(k in event['data'] for k in required):
                raise ValueError('Lần làm bài thiếu trường bắt buộc')
        if event['id'] in merged and merged[event['id']] != event:
            raise ValueError('Xung đột ID; không ghi đè lịch sử')
        merged[event['id']] = event
    return list(merged.values())
