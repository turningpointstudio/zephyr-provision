# Hyper-V VLAN Setup Guide

This guide explains how to set up VLANs in Hyper-V using the provided Ansible automation.

## Prerequisites

1. **Physical Network Requirements:**
   - Physical network adapter that supports 802.1q VLAN tagging
   - Network switch that supports 802.1q VLAN tagging
   - Proper VLAN configuration on your physical network infrastructure

2. **Windows Requirements:**
   - Windows 10 Pro/Enterprise or Windows Server 2016+
   - Hyper-V feature enabled
   - Administrative privileges

## Configuration Steps

### 1. Configure Variables

Edit `stage_machine/vars/main.yml` and uncomment/modify the following variables:

```yaml
# Physical network adapter name
hyperv_physical_adapter: "Ethernet"  # Use Get-NetAdapter to find your adapter

# External virtual switch (connects to physical network)
hyperv_external_switch_name: "External Switch"
hyperv_management_vlan_id: 1

# VM-specific VLAN configurations
hyperv_vm_vlans:
  - vm_name: "WebServer"
    vlan_id: 10
    switch_name: "External Switch"
  - vm_name: "DatabaseServer"
    vlan_id: 20
    switch_name: "External Switch"
```

### 2. Run the Ansible Playbook

```bash
ansible-playbook -i inventory.yml playbook.yml
```

## VLAN Configuration Types

### Access Mode (Single VLAN)
Each VM is assigned to a specific VLAN:

```yaml
hyperv_vm_vlans:
  - vm_name: "WebServer"
    vlan_id: 10
    switch_name: "External Switch"
```

### Trunk Mode (Multiple VLANs)
For VMs that need access to multiple VLANs (like routers):

```yaml
hyperv_trunk_vms:
  - vm_name: "RouterVM"
    allowed_vlans: ["10", "20", "30"]
    native_vlan: 0
    switch_name: "External Switch"
```

## Manual PowerShell Commands

If you prefer to configure VLANs manually, here are the key PowerShell commands:

### Create Virtual Switches
```powershell
# External switch (connects to physical network)
New-VMSwitch -Name "External Switch" -NetAdapterName "Ethernet" -AllowManagementOS $true

# Internal switch (host-only communication)
New-VMSwitch -Name "Internal Switch" -SwitchType Internal

# Private switch (VM-to-VM only)
New-VMSwitch -Name "Private Switch" -SwitchType Private
```

### Configure Management OS VLAN
```powershell
Set-VMNetworkAdapterVlan -ManagementOS -VMNetworkAdapterName "External Switch" -Access -VlanId 1
```

### Configure VM VLAN (Access Mode)
```powershell
Set-VMNetworkAdapterVlan -VMName "WebServer" -Access -VlanId 10
```

### Configure VM VLAN (Trunk Mode)
```powershell
Set-VMNetworkAdapterVlan -VMName "RouterVM" -Trunk -AllowedVlanIdList "10,20,30" -NativeVlanId 0
```

## Verification Commands

### Check Virtual Switches
```powershell
Get-VMSwitch
```

### Check VLAN Configurations
```powershell
# Management OS VLANs
Get-VMNetworkAdapter -ManagementOS | Get-VMNetworkAdapterVlan

# VM VLANs
Get-VM | Get-VMNetworkAdapter | Get-VMNetworkAdapterVlan
```

### Check Network Adapters
```powershell
Get-NetAdapter
```

## Troubleshooting

### Common Issues

1. **VLAN not working:**
   - Verify physical network adapter supports VLAN tagging
   - Check that physical switch is configured for the same VLANs
   - Ensure VLAN IDs match between Hyper-V and physical infrastructure

2. **Management OS loses network connectivity:**
   - Check that management VLAN ID is correct
   - Verify physical network configuration
   - Test with a simple VLAN ID (like 1) first

3. **VMs cannot communicate:**
   - Verify VLAN IDs are correctly assigned
   - Check that VMs are on the same VLAN if they need to communicate
   - Ensure virtual switches are properly configured

### Testing VLAN Configuration

1. **Test Management OS connectivity:**
   ```powershell
   Test-NetConnection -ComputerName 8.8.8.8
   ```

2. **Test VM connectivity:**
   - Ping from VM to gateway
   - Ping from VM to other VMs on same VLAN
   - Test connectivity to external resources

3. **Verify VLAN tagging:**
   - Use network monitoring tools to verify VLAN tags
   - Check switch logs for VLAN traffic

## Best Practices

1. **Planning:**
   - Document your VLAN scheme before implementation
   - Use consistent VLAN IDs across your infrastructure
   - Plan for management VLAN separate from VM VLANs

2. **Security:**
   - Use different VLANs for different security zones
   - Implement proper firewall rules between VLANs
   - Consider using private switches for sensitive VMs

3. **Management:**
   - Keep management OS on a dedicated VLAN
   - Use descriptive names for virtual switches
   - Document all VLAN assignments

## Example Scenarios

### Scenario 1: Simple Web/Database Setup
```yaml
hyperv_vm_vlans:
  - vm_name: "WebServer"
    vlan_id: 10
  - vm_name: "DatabaseServer"
    vlan_id: 20
  - vm_name: "LoadBalancer"
    vlan_id: 10
```

### Scenario 2: Multi-Tenant Environment
```yaml
hyperv_vm_vlans:
  - vm_name: "Tenant1-Web"
    vlan_id: 100
  - vm_name: "Tenant1-DB"
    vlan_id: 101
  - vm_name: "Tenant2-Web"
    vlan_id: 200
  - vm_name: "Tenant2-DB"
    vlan_id: 201
```

### Scenario 3: Router VM with Multiple VLANs
```yaml
hyperv_trunk_vms:
  - vm_name: "CoreRouter"
    allowed_vlans: ["10", "20", "30", "100", "200"]
    native_vlan: 0
```

This setup provides a comprehensive solution for managing Hyper-V VLANs through Ansible automation while maintaining flexibility for manual configuration when needed.
