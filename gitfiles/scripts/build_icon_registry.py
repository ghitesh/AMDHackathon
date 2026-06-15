from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from collections import defaultdict


ICON_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg"}


# ============================================================
# Manual Alias Definitions
# ============================================================

MANUAL_ALIASES = {
    "EC2": [
        "amazon ec2",
        "elastic compute cloud",
        "instance",
    ],
    "Lambda": [
        "aws lambda",
        "lambda function",
    ],
    "ECS": [
        "amazon ecs",
        "elastic container service",
    ],
    "EKS": [
        "amazon eks",
        "elastic kubernetes service",
    ],
    "S3": [
        "amazon s3",
        "simple storage service",
        "bucket",
    ],
    "RDS": [
        "amazon rds",
        "relational database service",
    ],
    "Aurora": [
        "amazon aurora",
    ],
    "DynamoDB": [
        "amazon dynamodb",
    ],
    "ALB": [
        "application load balancer",
        "alb",
    ],
    "NLB": [
        "network load balancer",
        "nlb",
    ],
    "CloudFront": [
        "cdn",
    ],
    "Route53": [
        "route 53",
        "dns",
    ],
    "VPC": [
        "virtual private cloud",
    ],
    "API Gateway": [
        "api gateway",
    ],
    "SQS": [
        "queue",
        "amazon sqs",
    ],
    "SNS": [
        "notification service",
        "amazon sns",
    ],
    "EventBridge": [
        "event bus",
    ],
    "Redshift": [
        "amazon redshift",
    ],
    "OpenSearch": [
        "elasticsearch",
        "amazon opensearch",
    ],
    "SageMaker": [
        "amazon sagemaker",
    ],
}


# ============================================================
# Service Name Extraction
# ============================================================

SERVICE_PATTERNS = [
    ("Amazon-EC2", "EC2"),
    ("Amazon-Simple-Storage-Service", "S3"),
    ("Amazon-DynamoDB", "DynamoDB"),
    ("Amazon-Aurora", "Aurora"),
    ("Amazon-RDS", "RDS"),
    ("Amazon-Elastic-Container-Service", "ECS"),
    ("Amazon-Elastic-Kubernetes-Service", "EKS"),
    ("Amazon-VPC", "VPC"),
    ("Amazon-CloudFront", "CloudFront"),
    ("Amazon-Route-53", "Route53"),
    ("Amazon-API-Gateway", "API Gateway"),
    ("AWS-Lambda", "Lambda"),
    ("Amazon-EventBridge", "EventBridge"),
    ("Amazon-Simple-Queue-Service", "SQS"),
    ("Amazon-Simple-Notification-Service", "SNS"),
    ("Amazon-Redshift", "Redshift"),
    ("Amazon-OpenSearch-Service", "OpenSearch"),
    ("Amazon-SageMaker", "SageMaker"),
]


def extract_service_name(filename: str) -> str:

    stem = Path(filename).stem

    for pattern, service in SERVICE_PATTERNS:
        if pattern in stem:
            return service

    stem = re.sub(r"^(Res_|Arch_)", "", stem)

    stem = re.sub(
        r"_(16|32|48|64|128)(@5x)?$",
        "",
        stem,
    )

    tokens = stem.split("_")

    if not tokens:
        return stem

    return tokens[0]


# ============================================================
# Metadata Extraction
# ============================================================

def determine_icon_type(path: Path) -> str:

    p = str(path)

    if "Resource-Icons" in p:
        return "resource"

    if "Architecture-Service-Icons" in p:
        return "service"

    if "Architecture-Group-Icons" in p:
        return "group"

    return "unknown"


def extract_category(path: Path) -> str:

    for part in path.parts:

        if part.startswith("Res_"):
            return part

        if part.startswith("Arch_"):
            return part

    return "Unknown"


def extract_size(filename: str):

    m = re.search(
        r"_(16|24|32|48|64|128)",
        filename,
    )

    if m:
        return int(m.group(1))

    return 0


# ============================================================
# Alias Generation
# ============================================================

def build_aliases(service: str):

    aliases = {
        service.lower(),
        service.replace("-", " ").lower(),
    }

    aliases.update(
        MANUAL_ALIASES.get(service, [])
    )

    return sorted(
        {
            a.lower().strip()
            for a in aliases
        }
    )


# ============================================================
# Icon Ranking
# ============================================================

def score_icon(icon):

    score = 0

    if icon["icon_type"] == "resource":
        score += 100

    elif icon["icon_type"] == "service":
        score += 50

    elif icon["icon_type"] == "group":
        score += 10

    score += icon["size"]

    return score


# ============================================================
# Catalog Builder
# ============================================================

class IconCatalogBuilder:

    def __init__(self, icon_root):

        self.icon_root = Path(icon_root)

    def build(self):

        services = defaultdict(list)

        for file in self.icon_root.rglob("*"):

            if not file.is_file():
                continue

            if file.suffix.lower() not in ICON_EXTENSIONS:
                continue

            service = extract_service_name(
                file.name
            )

            icon = {
                "service": service,
                "path": str(
                    file.relative_to(
                        self.icon_root
                    )
                ),
                "category": extract_category(
                    file
                ),
                "icon_type": determine_icon_type(
                    file
                ),
                "size": extract_size(
                    file.name
                ),
            }

            services[service].append(icon)

        return services


# ============================================================
# Main
# ============================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--icon-root",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    services = IconCatalogBuilder(
        args.icon_root
    ).build()

    preferred = {}

    alias_lookup = {}

    for service, icons in services.items():

        best = max(
            icons,
            key=score_icon,
        )

        aliases = build_aliases(
            service
        )

        best["aliases"] = aliases

        preferred[service] = best

        for alias in aliases:
            alias_lookup[alias] = service

    catalog = {
        "preferred": preferred,
        "aliases": alias_lookup,
    }

    with open(
        args.output,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            catalog,
            f,
            indent=2,
        )

    print(
        f"Generated catalog with "
        f"{len(preferred)} services"
    )


if __name__ == "__main__":
    main()