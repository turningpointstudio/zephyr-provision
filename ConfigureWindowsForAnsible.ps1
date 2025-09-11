<#
.SYNOPSIS
Securely bootstrap a Windows 11 machine for Ansible management.

.DESCRIPTION
- Enables WinRM over HTTPS.
- Generates a self-signed certificate for encrypted communication.
- Creates a dedicated 'ansible' user with administrative rights.
- Configures firewall rules for WinRM HTTPS.
#>

Write-Host "=== Secure Bootstrap for Ansible ==="

### STEP 1: Enable PSRemoting
Write-Host "Enabling PSRemoting..."
Enable-PSRemoting -Force

### STEP 2: Add HTTPS listener with a self signed certificate
Write-Host "Creating self-signed certificate..."
$certParams = @{
  CertStoreLocation = 'Cert:\LocalMachine\My'
  DnsName           = $env:COMPUTERNAME
  NotAfter          = (Get-Date).AddYears(1)
  Provider          = 'Microsoft Software Key Storage Provider'
  Subject           = "CN=$env:COMPUTERNAME"
}
$cert = New-SelfSignedCertificate @certParams

Write-Host "Creating HTTPS listener..."
$httpsParams = @{
  ResourceURI = 'winrm/config/listener'
  SelectorSet = @{
    Transport = "HTTPS"
    Address   = "*"
  }
  ValueSet    = @{
    CertificateThumbprint = $cert.Thumbprint
    Enabled               = $true
  }
}
New-WSManInstance @httpsParams

### STEP 3: Open firewall port for WinRM HTTPS
Write-Host "Opening firewall port 5986 for all profiles..."
$firewallParams = @{
  Action      = 'Allow'
  Description = 'Inbound rule for Windows Remote Management via WS-Management. [TCP 5986]'
  Direction   = 'Inbound'
  DisplayName = 'Windows Remote Management (HTTPS-In)'
  LocalPort   = 5986
  Profile     = @('Domain', 'Private', 'Public')
  Protocol    = 'TCP'
  Enabled     = $true
}
New-NetFirewallRule @firewallParams

### STEP 4: Create dedicated Ansible user
$Username = "ansible"
$PasswordPlain = "ansible2025!"
$Password = ConvertTo-SecureString $PasswordPlain -AsPlainText -Force

if (-not (Get-LocalUser -Name $Username -ErrorAction SilentlyContinue)) {
  Write-Host "Creating Ansible user '$Username'..."
  New-LocalUser -Name $Username -Password $Password -FullName "Ansible Automation User" `
    -Description "Dedicated user for Ansible automation"
  Add-LocalGroupMember -Group "Administrators" -Member $Username
  Write-Host "User '$Username' created and added to Administrators group."
}
else {
  Write-Host "User '$Username' already exists. Skipping creation."
}

### STEP 5: Ensure WinRM service is running
Write-Host "Starting WinRM service..."
Set-Service -Name WinRM -StartupType Automatic
Start-Service -Name WinRM

Write-Host "=== Secure Bootstrap Complete ==="