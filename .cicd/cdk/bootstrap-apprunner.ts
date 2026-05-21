import * as cdk from "aws-cdk-lib";
import * as apprunner from "aws-cdk-lib/aws-apprunner";
import * as ecr from "aws-cdk-lib/aws-ecr";
import * as iam from "aws-cdk-lib/aws-iam";
import { Tags } from "aws-cdk-lib";

export interface BootstrapAppRunnerProps {
  appName: string;
  environment: string;
  region: string;
  ecrRepoName: string;
}

export class BootstrapAppRunnerStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props: BootstrapAppRunnerProps) {
    super(scope, id, { env: { region: props.region } });

    Tags.of(this).add("cicd:app", props.appName);
    Tags.of(this).add("cicd:env", props.environment);
    Tags.of(this).add("cicd:managed-by", "aws-cicd-skill");

    const repo = new ecr.Repository(this, "EcrRepo", {
      repositoryName: props.ecrRepoName,
      imageScanOnPush: true,
      lifecycleRules: [{ maxImageCount: 20 }],
    });

    const accessRole = new iam.Role(this, "AppRunnerAccessRole", {
      assumedBy: new iam.ServicePrincipal("build.apprunner.amazonaws.com"),
    });
    repo.grantPull(accessRole);

    const instanceRole = new iam.Role(this, "AppRunnerInstanceRole", {
      assumedBy: new iam.ServicePrincipal("tasks.apprunner.amazonaws.com"),
    });

    const service = new apprunner.CfnService(this, "Service", {
      serviceName: `${props.appName}-${props.environment}`,
      sourceConfiguration: {
        authenticationConfiguration: {
          accessRoleArn: accessRole.roleArn,
        },
        imageRepository: {
          imageIdentifier: `${repo.repositoryUri}:latest`,
          imageRepositoryType: "ECR",
          imageConfiguration: { port: "8080" },
        },
        autoDeploymentsEnabled: false,
      },
      instanceConfiguration: {
        cpu: "1024",
        memory: "2048",
        instanceRoleArn: instanceRole.roleArn,
      },
    });

    new cdk.CfnOutput(this, "EcrRepositoryUri", { value: repo.repositoryUri });
    new cdk.CfnOutput(this, "AppRunnerServiceArn", { value: service.attrServiceArn });
    new cdk.CfnOutput(this, "AppRunnerServiceUrl", { value: service.attrServiceUrl });
    new cdk.CfnOutput(this, "SsmHandlesHint", {
      value: `/cicd/${props.appName}/${props.environment}/handles`,
      description: "Write handles JSON here after bootstrap",
    });
  }
}

const app = new cdk.App();
const appName = app.node.tryGetContext("appName") ?? "my-app";
const environment = app.node.tryGetContext("environment") ?? "dev";
const region = app.node.tryGetContext("region") ?? "us-east-1";

new BootstrapAppRunnerStack(app, "BootstrapAppRunner", {
  appName,
  environment,
  region,
  ecrRepoName: `${appName}-${environment}`,
});
