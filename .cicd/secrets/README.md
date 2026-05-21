# CI/CD Secret Boundary

Do not commit real secret values to `.cicd/`.

The generated environment files may store secret names, variable names, and ARN references only. Real values belong in GitHub Secrets, GitHub Variables, AWS Secrets Manager, or AWS Systems Manager Parameter Store.

## GitHub Secrets

- `AWS_RELEASE_ROLE_ARN`: IAM role ARN trusted by GitHub OIDC for release and deploy workflows.
- `AWS_EC2_SSH_PRIVATE_KEY`: private key for EC2 SSH deployment, required only when `deployment.target` is `ec2-ssh`.

## GitHub Variables

Define only the variables needed by enabled services:

- `AWS_REGION`
- `ECR_REPOSITORY_FRONTEND`
- `ECR_REPOSITORY_BACKEND`
- `ECR_REPOSITORY_WORKER`

## AWS Secret Stores

Application runtime values should live in AWS Secrets Manager or SSM Parameter Store:

- database credentials
- application runtime secrets
- third-party API keys
- OAuth credentials

Reference these values by name or ARN in `.cicd/env/<environment>.yaml`.

## CloudWatch Logs 写入权限（EC2 实例角色）

当 `.cicd/env/<env>.yaml` 中 `logging.cloudwatch.enabled` 为 `true` 时，
Docker 的 awslogs 日志驱动会直接调用 AWS CloudWatch Logs API 推送日志，
因此 EC2 实例的 IAM 角色需要以下权限：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "<ARN_PREFIX>:logs:<REGION>:<ACCOUNT_ID>:log-group:/ecs/<project>*:*"
        }
    ]
}
```

建议将 Resource 收窄到具体的 log group 前缀，不要使用 `"*"`。

此权限由 EC2 实例角色承担，不需要在 GitHub Actions 中配置额外的 Secret。
