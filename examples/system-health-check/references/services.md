# Services to Monitor

## Production Services
```
# Format: service_name,environment,slack_channel,runbook_link
api,production,#incidents,https://wiki.company.com/runbooks/api
web,production,#incidents,https://wiki.company.com/runbooks/web
worker,production,#incidents,https://wiki.company.com/runbooks/worker
```

## Service Dependencies
```
# Format: service_name,depends_on
api,database|redis|auth-service
web,api|cdn
worker,database|message-queue
```

## Escalation Contacts
```
# Format: service,on-call-channel,backup-contact
api,#api-oncall,devops@company.com
web,#web-oncall,devops@company.com
worker,#worker-oncall,devops@company.com
```

## Dashboard Links
- Grafana: https://grafana.company.com/d/prod-dashboard
- DataDog: https://app.datadoghq.com/dashboard/prod
- New Relic: https://one.newrelic.com
