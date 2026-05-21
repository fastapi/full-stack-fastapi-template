import * as cdk from "aws-cdk-lib";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as elbv2 from "aws-cdk-lib/aws-elasticloadbalancingv2";
import { Tags } from "aws-cdk-lib";

export interface ImportExistingProps {
  appName: string;
  environment: string;
  region: string;
  clusterName: string;
  clusterArn: string;
  vpcArn: string;
  targetGroupArn: string;
  albArn: string;
}

/** Import existing ECS/ALB resources — never creates new Cluster(). */
export class ImportExistingStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props: ImportExistingProps) {
    super(scope, id, { env: { region: props.region } });

    Tags.of(this).add("cicd:app", props.appName);
    Tags.of(this).add("cicd:env", props.environment);
    Tags.of(this).add("cicd:managed-by", "aws-cicd-skill");

    const vpc = ec2.Vpc.fromVpcAttributes(this, "ImportedVpc", {
      vpcId: app.node.tryGetContext("vpcId") ?? "vpc-placeholder",
      availabilityZones: ["us-east-1a", "us-east-1b"],
    });
    const cluster = ecs.Cluster.fromClusterAttributes(this, "ImportedCluster", {
      clusterName: props.clusterName,
      clusterArn: props.clusterArn,
      vpc,
    });

    const tg = elbv2.ApplicationTargetGroup.fromTargetGroupAttributes(this, "ImportedTg", {
      targetGroupArn: props.targetGroupArn,
    });

    elbv2.ApplicationLoadBalancer.fromApplicationLoadBalancerAttributes(this, "ImportedAlb", {
      loadBalancerArn: props.albArn,
      securityGroupId: "sg-placeholder",
    });

    new cdk.CfnOutput(this, "ImportedClusterArn", { value: cluster.clusterArn });
    new cdk.CfnOutput(this, "ImportedTargetGroupArn", { value: tg.targetGroupArn });
    new cdk.CfnOutput(this, "SsmHandlesPath", {
      value: `/cicd/${props.appName}/${props.environment}/handles`,
    });
  }
}

const app = new cdk.App();
new ImportExistingStack(app, "ImportExisting", {
  appName: app.node.tryGetContext("appName") ?? "my-app",
  environment: app.node.tryGetContext("environment") ?? "dev",
  region: app.node.tryGetContext("region") ?? "us-east-1",
  clusterName: app.node.tryGetContext("clusterName") ?? "cluster",
  clusterArn: app.node.tryGetContext("clusterArn") ?? "<ARN>/cluster",
  vpcArn: app.node.tryGetContext("vpcArn") ?? "<ARN>/vpc",
  targetGroupArn: app.node.tryGetContext("targetGroupArn") ?? "<ARN>/target-group",
  albArn: app.node.tryGetContext("albArn") ?? "<ARN>/alb",
});
