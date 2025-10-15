# Circular Dependency Solution

## Problem
Workstations and stage_machines need to map network drives from each other, creating a circular dependency:
- Workstations → need shares from stage_machines
- Stage_machines → need shares from workstations

## Solution: Two-Phase Provisioning

### Phase 1: Setup & Share Creation
All machines are provisioned with their roles BUT network drive mapping is skipped using conditional flags:
- `stage_machines_skip_drive_mapping: true`
- `workstations_skip_drive_mapping: true`

This ensures all shares are created and available before any machine tries to map them.

### Phase 2: Network Drive Mapping
After all shares exist, we run the drive mapping tasks on all machines:
- Stage machines map drives from workstations
- Workstations map drives from stage machines

## How It Works

### provision.yml Structure
```yaml
# Phase 1: Create shares (skip drive mapping)
- hosts: stage_machines
  roles:
    - role: stage_machines
      stage_machines_skip_drive_mapping: true

- hosts: workstations
  roles:
    - role: workstations
      workstations_skip_drive_mapping: true

# Phase 2: Map drives (shares now exist)
- hosts: stage_machines
  tasks:
    - include_role:
        name: stage_machines
        tasks_from: map_network_drives.yml

- hosts: workstations
  tasks:
    - include_role:
        name: workstations
        tasks_from: map_network_drives.yml
```

### Role Task Files
Both role main.yml files use a conditional when clause:
```yaml
when: workstations_tasks != 'map_network_drives.yml' or not (workstations_skip_drive_mapping | default(false))
```

This skips the map_network_drives.yml task when the skip flag is true.

## Benefits
- ✅ No circular dependency
- ✅ Clean separation of concerns
- ✅ All shares exist before mapping
- ✅ Easy to understand and maintain
- ✅ Can be run repeatedly (idempotent)

## Alternative Solutions

### Option 2: Separate Playbooks
Create two playbooks:
1. `provision-shares.yml` - Sets up all machines except drive mapping
2. `provision-drives.yml` - Only maps network drives

Run them sequentially:
```bash
ansible-playbook provision-shares.yml
ansible-playbook provision-drives.yml
```

### Option 3: Error Handling with Retries
Use `ignore_errors` and retry logic, but this is less clean and may hide real errors.

## Testing
To test the full provisioning:
```bash
ansible-playbook -i inventory.yml provision.yml
```

The playbook will automatically handle the two-phase provisioning.

