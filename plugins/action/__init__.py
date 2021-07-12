import sqlite3
from typing import List, Dict, Optional
from abc import abstractmethod
from dataclasses import dataclass, asdict
from os import path, mkdir
from ansible.plugins.action import ActionBase

class Status:
    OK = 'ok'
    Warning = 'warn'
    Error = 'error'

class ItemType:
    Host = 'host'

StatusText = {
    Status.OK: 'Operational',
    Status.Warning: 'Warning',
    Status.Error: 'Error'
}

StatusStrength = [
    Status.OK,
    Status.Warning,
    Status.Error
]

@dataclass
class Item:
    name: str
    status: Status
    quick_info: Optional[str]
    detailed_info: Optional[str]

@dataclass
class Group:
    title: str
    status: Status
    items: Dict[str, Item]

@dataclass
class TemplateData:
    system_name: str
    summary: str
    last_update: str
    status: Status
    groups: Dict[str, Group]


class FlightdekActionBase(ActionBase):
    def __init__(self, *args, **kwargs):
        super(FlightdekActionBase, self).__init__(*args, **kwargs)

        self._db = None
        self._output_folder = None
        self._args = None

    def run(self, tmp=None, task_vars=None):
        super(FlightdekActionBase, self).run(tmp, task_vars)

        self._args = self._task.args.copy()
        output_folder = self._args.get('output_folder', None)
        if output_folder is None:
            output_folder = path.join(task_vars.get('playbook_dir'), 'flightdek')

        self._output_folder = path.expanduser(output_folder)

        if not path.exists(self.output_folder):
            mkdir(self.output_folder)

        self._init_db()

        return self.inner_run()

    @property
    def db(self):
        return self._db

    @property
    def output_folder(self):
        return self._output_folder

    @property
    def args(self):
        return self._args

    @abstractmethod
    def inner_run(self):
        pass

    def _init_db(self):
        data_file = path.join(self.output_folder, f'flightdek.db')

        new_db = not path.exists(data_file)
        self._db = sqlite3.connect(data_file)

        if new_db:
            cursor = self.db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    'id' INTEGER PRIMARY KEY AUTOINCREMENT,
                    'type' TEXT not null,
                    'name' TEXT not null,
                    'group' TEXT not null,
                    'status' TEXT not null,
                    'extra' TEXT,
                    'date_added' INTEGER not null
                );
            ''')

            self.db.commit()

