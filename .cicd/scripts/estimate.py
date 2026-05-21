"""Monthly cost estimate (pure math, no AWS API calls)."""

from __future__ import annotations

import argparse

# Public list prices (USD/month, approximate) — update in one place
APPRUNNER_VCPU_HOUR = 0.064
APPRUNNER_GB_HOUR = 0.007
ECS_VCPU_HOUR = 0.04048
ECS_GB_HOUR = 0.004445
ALB_MONTHLY = 16.0
NAT_MONTHLY = 32.0
CW_LOGS_GB = 0.50


def estimate_apprunner(vcpu: float = 1.0, memory_gb: float = 2.0, hours: float = 24 * 30) -> dict:
    compute = vcpu * APPRUNNER_VCPU_HOUR * hours + memory_gb * APPRUNNER_GB_HOUR * hours
    return {"target": "apprunner", "monthly_usd": round(compute, 2), "breakdown": {"compute": round(compute, 2)}}


def estimate_ecs(
    vcpu: float = 0.5,
    memory_gb: float = 1.0,
    tasks: int = 1,
    include_alb: bool = True,
    include_nat: bool = True,
    log_gb: float = 5.0,
) -> dict:
    hours = 24 * 30
    compute = tasks * (vcpu * ECS_VCPU_HOUR * hours + memory_gb * ECS_GB_HOUR * hours)
    alb = ALB_MONTHLY if include_alb else 0
    nat = NAT_MONTHLY if include_nat else 0
    logs = log_gb * CW_LOGS_GB
    total = compute + alb + nat + logs
    return {
        "target": "ecs-fargate",
        "monthly_usd": round(total, 2),
        "breakdown": {
            "fargate": round(compute, 2),
            "alb": alb,
            "nat": nat,
            "logs": round(logs, 2),
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--target", choices=["apprunner", "ecs-fargate"], default="apprunner")
    p.add_argument("--cpu", type=float, default=1.0)
    p.add_argument("--memory", type=float, default=2.0, help="GB")
    args = p.parse_args()
    if args.target == "apprunner":
        r = estimate_apprunner(args.cpu, args.memory)
    else:
        r = estimate_ecs(vcpu=args.cpu, memory_gb=args.memory)
    print(f"**Estimated monthly cost:** ${r['monthly_usd']}")
    for k, v in r["breakdown"].items():
        print(f"- {k}: ${v}")


if __name__ == "__main__":
    main()
