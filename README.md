Step 1: Provision Hosts
- Make sure you are connected to the internet
- Run bootstrap.cmd as admin

Step 2:
Create inventory file (this changes per deployment)

Step 3:
Define roles for repeatable configurations (workstation, userstation, mediaserver, etc.)
An example of this would be:
- name: Configure workstations
  hosts: all
  roles:
    - dev-workstation
    - general-hardening

Step 4:
Run it
ansible-playbook -i inventory-this-week.yml setup.yml

Overview:
bootstrap.ps1 run once per fresh install.
inventory-week.yml generated/edited per batch.
setup.yml playbook applies reusable roles.