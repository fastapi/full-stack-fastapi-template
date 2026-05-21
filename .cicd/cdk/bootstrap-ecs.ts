import * as cdk from "aws-cdk-lib";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as elbv2 from "aws-cdk-lib/aws-elasticloadbalancingv2";
import * as ecr from "aws-cdk-lib/aws-ecr";
import * as logs from "aws-cdk-lib/aws-logs";
import { Tags } from "aws-cdk-lib";

export interface BootstrapEcsProps {
  appName: string;
  environment: string;
  region: string;
  vpcId?: string;
}

export class BootstrapEcsStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props: BootstrapEcsProps) {
    super(scope, id, { env: { region: props.region } });

    Tags.of(this).add("cicd:app", props.appName);
    Tags.of(this).add("cicd:env", props.environment);
    Tags.of(this).add("cicd:managed-by", "aws-cicd-skill");

    const vpc = props.vpcId
      ? ec2.Vpc.fromLookup(this, "Vpc", { vpcId: props.vpcId })
      : new ec2.Vpc(this, "Vpc", { maxAzs: 2, natGateways: 1 });

    const repo = new ecr.Repository(this, "EcrRepo", {
      repositoryName: `${props.appName}-${props.environment}`,
      imageScanOnPush: true,
    });

    const cluster = new ecs.Cluster(this, "Cluster", {
      vpc,
      clusterName: `${props.appName}-${props.environment}`,
      containerInsights: true,
    });

    const taskDef = new ecs.FargateTaskDefinition(this, "TaskDef", {
      cpu: 512,
      memoryLimitMiB: 1024,
    });
    taskDef.addContainer("App", {
      image: ecs.ContainerImage.fromEcrRepository(repo, "latest"),
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: props.appName,
        logRetention: logs.RetentionDays.ONE_MONTH,
      }),
      portMappings: [{ containerPort: 8080 }],
    });

    const service = new ecs.FargateService(this, "Service", {
      cluster,
      taskDefinition: taskDef,
      desiredCount: 1,
      assignPublicIp: true,
    });

    const alb = new elbv2.ApplicationLoadBalancer(this, "Alb", { vpc, internetFacing: true });
    const listener = alb.addListener("Http", { port: 80, open: true });
    const tg = listener.addTargets("EcsTargets", {
      port: 8080,
      targets: [service],
      healthCheck: { path: "/health" },
    });

    new cdk.CfnOutput(this, "ClusterName", { value: cluster.clusterName });
    new cdk.CfnOutput(this, "TargetGroupArn", { value: tg.targetGroupArn });
    new cdk.CfnOutput(this, "EcrRepositoryUri", { value: repo.repositoryUri });
  }
}

const app = new cdk.App();
const appName = app.node.tryGetContext("appName") ?? "my-app";
const environment = app.node.tryGetContext("environment") ?? "dev";
const region = app.node.tryGetContext("region") ?? "us-east-1";

new BootstrapEcsStack(app, "BootstrapEcs", {
  appName,
  environment,
  region,
  vpcId: app.node.tryGetContext("vpcId"),
});
