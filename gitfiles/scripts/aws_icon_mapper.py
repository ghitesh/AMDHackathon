from pathlib import Path


ICON_MAP = {
    "EC2": "Amazon-EC2.png",
    "RDS": "Amazon-RDS.png",
    "S3": "Amazon-S3.png",
    "ALB": "Elastic-Load-Balancing.png",
    "Lambda": "AWS-Lambda.png",
    "DynamoDB": "Amazon-DynamoDB.png"
}


def get_icon(service, icon_root):
    filename = ICON_MAP.get(service)

    if not filename:
        return None

    return Path(icon_root) / filename
