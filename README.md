# flightdek
Create beautiful status pages directly from Ansible

## Getting started
First, create your ansible project folder

```bash
$ mkdir ~/my-status-page
$ cd ~/my-status-page
$ python3 -m venv venv
$ source venv/bin/activate
```

Install Ansible >= 3.0 and Flightdek
```bash
(venv)$ pip install ansible
(venv)$ ansible-galaxy collection install https://github.com/navad/flightdek
```

### Creating simple Flightdek playbook
For example, using the following hosts file:
```ini
localhost ansible_connection=local
```

```yaml
# playbook.yml

- name: Check machines
  hosts: all
  gather_facts: no
  ignore_unreachable: yes

  tasks:
    - name: Ping machines
      ansible.builtin.ping:
      register: ping_res

    - name: Add to dek
      flightdek.core.add_item:
        name: '{{ inventory_hostname }}'
        group: Hosts
        warn_when: '{{ ping_res.failed }}'

- name: Wrap up
  hosts: localhost
  post_tasks:
  - name: Generate Report
    run_once: yes
    flightdek.core.render:
      filename: status.html
      title: My Status Page
    register: report_output

  - name: Open page
    ansible.builtin.command: 'open {{ report_output.status_page_file }}'
```

### Running Flightdek playbook
```bash
(venv)$ ansible-playbook -i hosts playbook.yml
```

After the playbook finishes running, Flihtdek's status page will be opened by the browser
