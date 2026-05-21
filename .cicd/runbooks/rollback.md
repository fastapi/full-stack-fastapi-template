# Rollback Runbook

## When To Roll Back

- Deployment workflow fails after updating infrastructure.
- Health or smoke verification fails.
- Error rate, latency, or business smoke checks exceed the configured threshold.
- A secret or configuration issue is detected after release.

## ECS

The deploy workflow automatically attempts this path when verification fails after an ECS service update:

1. Read the previous task definition from the rollback baseline captured before deploy.
2. Update the ECS service back to the previous task definition.
3. Wait for service stability.
4. Re-run health checks.
5. Save `rollback-evidence.json`.

Manual command shape:

```bash
aws ecs update-service \
  --cluster "$ECS_CLUSTER" \
  --service "$ECS_SERVICE" \
  --task-definition "$PREVIOUS_TASK_DEFINITION"

aws ecs wait services-stable \
  --cluster "$ECS_CLUSTER" \
  --services "$ECS_SERVICE"
```

## EC2 SSH

The deploy workflow automatically attempts this path when verification fails after an EC2 container restart:

1. Read the previous image from the rollback baseline captured before deploy.
2. SSH to affected hosts.
3. Pull and restart the previous image.
4. Re-run host health checks.
5. Save `rollback-evidence.json`.

Manual command shape:

```bash
ssh "$SSH_USER@$HOST" "
  docker pull '$PREVIOUS_IMAGE' &&
  docker rm -f '$CONTAINER_NAME' || true &&
  docker run -d --restart unless-stopped --name '$CONTAINER_NAME' '$PREVIOUS_IMAGE'
"
```

## Evidence Files

- `deployment-evidence.json`: target environment, release ID, image digests, service revisions, target health, HTTP verification, and workflow URL.
- `rollback-evidence.json`: previous task definitions or image digests and rollback status per service or host.

## Stop Conditions

- Do not retry blindly after two failures with the same root cause.
- Escalate if rollback cannot restore healthy service.
- Do not expose production traffic until verification passes.
- Do not assume database rollback is safe after destructive migrations.
