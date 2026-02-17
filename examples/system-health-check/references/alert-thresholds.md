# System Health Check Alert Thresholds

## Application Performance
| Metric | Warning | Critical | Duration |
|--------|---------|----------|----------|
| Response time p95 | >500ms | >1000ms | 5 min avg |
| Response time p99 | >1000ms | >2000ms | 5 min avg |
| Error rate (4xx+5xx) | >0.5% | >1% | 5 min avg |
| Request throughput drop | >30% | >50% | vs baseline |

## Infrastructure Health
| Metric | Warning | Critical | Duration |
|--------|---------|----------|----------|
| CPU usage | >70% | >85% | Sustained |
| Memory usage | >80% | >90% | Sustained |
| Disk space free | <20% | <10% | Immediate |
| Network latency | >100ms | >200ms | 5 min avg |

## Service Dependencies
| Metric | Warning | Critical | Duration |
|--------|---------|----------|----------|
| Database connections | >80% pool | >95% pool | Sustained |
| Redis cache hit rate | <80% | <60% | 5 min avg |
| External API latency | >1000ms | >2000ms | 5 min avg |
| Message queue depth | >1000 msgs | >5000 msgs | Sustained |

## Alert Priority Mapping
- **Warning** → PagerDuty P3 (Low)
- **Critical** → PagerDuty P2 (High)

## False Positive Prevention
- Ignore transient spikes (<2 minutes)
- Use 5-minute moving average
- Suppress duplicate alerts within 10 minutes
- Skip alerts during maintenance windows
