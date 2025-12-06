# Zephyr Multi-Instance Setup with nginx Load Balancer

This setup allows you to run multiple isolated Zephyr instances behind an nginx load balancer, enabling horizontal scaling and high availability.

## Architecture

```
ZephyrTracker Plugin (Deadline)
        ↓ (port 3001)
nginx Load Balancer
        ↓ (distributes to)
    ┌───┴───┬───────┬─────────┐
Instance 1  Instance 2  ...  Instance 8
(port 3002) (port 3003)      (port 3009)
```

## Files Overview

- `compose-nginx.yml` - nginx load balancer service
- `nginx.conf` - nginx configuration with upstream definitions
- `compose-instance-template.yml` - Template for creating new instances
- `compose-instance-1.yml` - Example instance 1
- `compose-instance-2.yml` - Example instance 2
- `.env.instance-1` - Environment variables for instance 1
- `.env.instance-2` - Environment variables for instance 2

## Quick Start

### 1. Start the nginx Load Balancer

First, create the shared network and start nginx:

```bash
docker-compose -f compose-nginx.yml up -d
```

### 2. Start Individual Instances

Start as many instances as you need:

```bash
# Start instance 1
docker-compose -f compose-instance-1.yml up -d

# Start instance 2
docker-compose -f compose-instance-2.yml up -d

# Start more instances...
docker-compose -f compose-instance-3.yml up -d
```

### 3. Verify Setup

Check that all services are running:

```bash
docker ps
```

Test the load balancer:

```bash
curl http://localhost:3001/nginx-health
```

## Creating Additional Instances

### Method 1: Copy Template

1. Copy `compose-instance-template.yml`:
   ```bash
   cp compose-instance-template.yml compose-instance-3.yml
   ```

2. Edit the new file and change:
   - `name: zephyr-instance-3`
   - Container names: `mongodb-instance-3`, `zephyr-instance-3`
   - Ports: `27013:27017` and `3004:3001`
   - Volume names: `db-data-instance-3`
   - Env file: `.env.instance-3`

3. Copy and edit environment file:
   ```bash
   cp .env.instance-1 .env.instance-3
   ```

4. Update `.env.instance-3`:
   - `TENANT_ID` - New tenant ID
   - `TENANT_NAME` - instance-3
   - `MONGO_URI` - mongodb://localhost:27013
   - `EXTERNAL_*` paths - Point to different directories
   - Other tenant-specific settings

5. Update `nginx.conf` to include the new instance:
   ```nginx
   upstream zephyr_backend {
       server host.docker.internal:3002 max_fails=3 fail_timeout=30s;
       server host.docker.internal:3003 max_fails=3 fail_timeout=30s;
       server host.docker.internal:3004 max_fails=3 fail_timeout=30s;  # NEW
   }
   ```

6. Reload nginx:
   ```bash
   docker-compose -f compose-nginx.yml restart
   ```

7. Start the new instance:
   ```bash
   docker-compose -f compose-instance-3.yml up -d
   ```

## Port Mapping Reference

| Instance | Zephyr Port | MongoDB Port | nginx Upstream |
|----------|-------------|--------------|----------------|
| 1        | 3002        | 27011        | host.docker.internal:3002 |
| 2        | 3003        | 27012        | host.docker.internal:3003 |
| 3        | 3004        | 27013        | host.docker.internal:3004 |
| 4        | 3005        | 27014        | host.docker.internal:3005 |
| 5        | 3006        | 27015        | host.docker.internal:3006 |
| 6        | 3007        | 27016        | host.docker.internal:3007 |
| 7        | 3008        | 27017        | host.docker.internal:3008 |
| 8        | 3009        | 27018        | host.docker.internal:3009 |

## Managing Instances

### Start/Stop Individual Instances

```bash
# Stop instance 2 (removes it from load balancer pool)
docker-compose -f compose-instance-2.yml down

# Start instance 2
docker-compose -f compose-instance-2.yml up -d
```

### View Logs

```bash
# nginx logs
docker-compose -f compose-nginx.yml logs -f

# Instance logs
docker-compose -f compose-instance-1.yml logs -f
```

### Stop Everything

```bash
# Stop all instances
docker-compose -f compose-instance-1.yml down
docker-compose -f compose-instance-2.yml down
# ... etc

# Stop nginx
docker-compose -f compose-nginx.yml down
```

## Load Balancing Strategies

Edit `nginx.conf` to change load balancing behavior:

### Round-robin (default)
Distributes requests evenly across all instances.

```nginx
upstream zephyr_backend {
    server host.docker.internal:3002;
    server host.docker.internal:3003;
}
```

### Least Connections
Sends requests to the instance with fewest active connections.

```nginx
upstream zephyr_backend {
    least_conn;
    server host.docker.internal:3002;
    server host.docker.internal:3003;
}
```

### IP Hash
Same client IP always goes to the same instance (sticky sessions).

```nginx
upstream zephyr_backend {
    ip_hash;
    server host.docker.internal:3002;
    server host.docker.internal:3003;
}
```

## Troubleshooting

### Instance not receiving traffic

1. Check if instance is running:
   ```bash
   docker ps | grep zephyr-instance
   ```

2. Check if instance is in nginx upstream:
   ```bash
   docker exec zephyr-nginx cat /etc/nginx/nginx.conf
   ```

3. Test instance directly:
   ```bash
   curl http://localhost:3002/health
   ```

### nginx returns 502 Bad Gateway

- Instance is down or unreachable
- Check instance logs: `docker-compose -f compose-instance-X.yml logs`
- Verify network connectivity

### Volumes/Data Isolation

Each instance has its own:
- MongoDB database (separate volume)
- File system mounts (configured in .env)
- Network namespace (isolated via Docker networks)

## ZephyrTracker Configuration

The ZephyrTracker Deadline plugin sends render events to port 3001, which nginx receives and distributes across all running instances.

No changes needed to ZephyrTracker configuration - it continues to send to:
```
http://<workstation-ip>:3001/<tenant-id>/renders
```

nginx automatically handles the distribution.

## Performance Considerations

- Each instance runs independently with its own MongoDB
- nginx adds minimal latency (<5ms)
- Scale horizontally by adding more instances
- Monitor instance load and adjust as needed
- Consider using `least_conn` for better distribution under varying load

## Security Notes

- All services run on host network for simplicity
- Consider adding authentication/API keys for production
- MongoDB instances are exposed on host ports (27011-27018) - restrict access if needed
- Use environment variables for sensitive data (don't commit .env files with real credentials)
