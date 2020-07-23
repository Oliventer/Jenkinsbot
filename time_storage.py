from datetime import datetime, timedelta
import heapq
import json


class SessionError(Exception):
    pass


class SessionAlreadyExist(SessionError):
    pass


class SessionDoesNotExist(SessionError):
    pass


class TimeStorage:
    def __init__(self, filename, storage=None):
        self.filename = filename
        self._active_since = {}
        self._storage = storage or {}

    @classmethod
    def from_json(cls, filename):
        with open(filename, encoding='utf-8') as f:
            raw_data = json.load(f)
        time_data = {int(k): timedelta(seconds=v) for k, v in raw_data.items()}
        return cls(filename, time_data)

    def save(self):
        self.close_all_sessions()
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self._storage, f, indent=4, default=lambda t: int(t.total_seconds()))

    def session_exist(self, member_id):
        return self._active_since.get(member_id) is not None

    def start_session(self, member_id, exists_ok=False):
        if self.session_exist(member_id) and not exists_ok:
            raise SessionAlreadyExist(f'Session with id {member_id} already exists')
        self._active_since[member_id] = datetime.now()

    def end_session(self, member_id):
        if not self.session_exist(member_id):
            raise SessionDoesNotExist(f'Session with id {member_id} does not exists')
        delta = datetime.now() - self._active_since[member_id]
        del self._active_since[member_id]
        already_timed = self._storage.get(member_id, timedelta())
        self._storage[member_id] = already_timed + delta

    def restart_session(self, member_id):
        if not self.session_exist(member_id):
            raise SessionDoesNotExist(f'Session with id {member_id} does not exists')
        self.end_session(member_id)
        self.start_session(member_id)

    def close_all_sessions(self):
        for member_id in self._active_since.copy().keys():
            self.end_session(member_id)

    def total_time(self, member_id):
        if self.session_exist(member_id):
            self.restart_session(member_id)
        return self._storage[member_id]

    def get_top_member_ids(self, length):
        active_members_ids = self._active_since.keys()
        # Taking current session time into account
        for member_id in active_members_ids:
            self.restart_session(member_id)
        return heapq.nlargest(length, self._storage, key=self._storage.get)

