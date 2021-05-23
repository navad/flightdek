from __future__ import (absolute_import, division, print_function)
from sqlite3.dbapi2 import Error
from typing import Dict
from os import path
from datetime import datetime, timedelta

from dataclasses import asdict

from ansible_collections.flightdek.core.templates import get_env
from ansible_collections.flightdek.core.plugins.action import FlightdekActionBase, Status, StatusText, StatusStrength, TemplateData, Group, Item

Summary = {
    Status.OK: 'All Systems Operational',
    Status.Warning: 'Degraded Service',
    Status.Error: 'Service Outage'
}

class ActionModule(FlightdekActionBase):
    def inner_run(self):
        cursor = self.db.cursor()
        now = datetime.now()

        min_timestamp = (now - timedelta(hours=1)).timestamp()
        cursor.execute('SELECT * FROM items WHERE date_added >= :min_timestamp ORDER BY date_added DESC', {
            'min_timestamp': min_timestamp
        })

        groups: Dict[str, Group] = dict()

        for row in cursor:
            (_, item_type, name, group, status, extra, date_added) = row
            current_group = groups.get(group, Group(
                title=group if group is not None else 'Ungrouped',
                status=Status.OK,
                items=dict()
            ))

            if name not in current_group.items:
                current_group.items[name] = Item(
                    name=name,
                    status=status,
                    status_text=StatusText[status]
                )

                most_severe_item = max(current_group.items.values(), key=lambda x: StatusStrength.index(x.status))
                current_group.status = most_severe_item.status

                groups[group] = current_group

        most_severe_group = max(groups.values(), key=lambda x: StatusStrength.index(x.status))

        template_data = TemplateData(
            system_name=self.args.get('title', ''),
            summary=Summary[most_severe_group.status],
            last_update=now.strftime('%b %d %Y, %H:%M:%S'),
            status=most_severe_group.status,
            groups=groups
        )

        filename = self.args.get('filename', f'status_{int(now.timestamp())}.html')
        full_filename = path.join(self.output_folder, filename)

        with open(full_filename, 'w') as f:
            env = get_env()
            t = env.get_template('main.html')
            f.write(t.render(asdict(template_data)))

        return dict(status_page_file=full_filename)

