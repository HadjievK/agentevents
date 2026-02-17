# Incident Response Runbook

## High Response Time (p95 > 1000ms)

### Check
1. Review recent deployments (last 2 hours)
2. Check database slow query logs
3. Look for traffic spikes in metrics dashboard
4. Verify no external API timeouts

### Remediation
- **If traffic spike**: Scale up instances
- **If slow query**: Add database index or kill blocking query
- **If deployment issue**: Consider rollback
- **If external API**: Implement circuit breaker

## High Error Rate (>1%)

### Check
1. Identify failing endpoints
2. Review application error logs
3. Check service dependencies (DB, Redis, etc.)
4. Look for DDoS patterns

### Remediation
- **If application error**: Review logs and fix issue
- **If dependency down**: Failover or degrade gracefully
- **If DDoS**: Contact security team
- **Recovery**: Deploy fix and monitor for regression

## High CPU/Memory Usage

### Check
1. Identify consuming process
2. Review recent code changes
3. Check for memory leaks
4. Verify no infinite loops

### Remediation
- **If memory leak**: Restart service (temporary), deploy fix
- **If infinite loop**: Kill process, deploy hotfix
- **If growth expected**: Scale infrastructure
- **After fix**: Monitor trending

## Critical Disk Space

### Check
1. Identify large directories
2. Review logs and cache growth
3. Check for disk leaks

### Remediation
- **Immediate**: Archive/delete old logs
- **Urgent**: Scale disk capacity
- **Fix**: Implement log rotation
- **Permanent**: Adjust retention policies

## Communication Template
```
🚨 [P2] {Service} {Metric} Degradation

Duration: {minutes} minutes
Threshold: {threshold}
Current: {value}

🔍 Likely cause: {cause}
✅ Action taken: {action}
📈 Monitoring: {dashboard_link}
```
