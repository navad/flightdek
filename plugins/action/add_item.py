from __future__ import (absolute_import, division, print_function)
import time

from ansible_collections.flightdek.core.plugins.action import ItemType, Status, FlightdekActionBase

class ActionModule(FlightdekActionBase):
    def inner_run(self):
        cursor = self.db.cursor()

        group_name = self.args.get('group', 'Ungrouped')

        is_error = bool(self.args.get('error_when', False))
        is_warn = bool(self.args.get('warn_when', False))

        status = Status.OK
        if is_warn:
            status = Status.Warning

        if is_error:
            status = Status.Error

        cursor.execute('insert into items values (:id, :type, :name, :group, :status, :extra, :date_added)', {
            'id': None,
            'type': ItemType.Host,
            'name': self.args.get('name', 'Untitled'),
            'group': group_name,
            'status': status,
            'extra': None,
            'date_added': int(time.time())
        })

        self.db.commit()
        self.db.close()

        return dict(ansible_facts={ })