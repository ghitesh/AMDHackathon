from pathlib import Path


ICON_MAP = {
    "EC2": "Architecture-Group-Icons_04302026/EC2-instance-contents_32.png",
    "RDS": "Resource-Icons_04302026/Res_Databases/Res_Amazon-Aurora_Amazon-RDS-Instance_48.png",
    "S3": "Architecture-Service-Icons_04302026/Arch_Storage/48/Arch_Amazon-Simple-Storage-Service_48.png",
    "ALB": "Resource-Icons_04302026/Res_Networking-Content-Delivery/Res_Elastic-Load-Balancing_Network-Load-Balancer_48.png",
    "Lambda": "Resource-Icons_04302026/Res_Compute/Res_AWS-Lambda_Lambda-Function_48.png",
    "DynamoDB": "Architecture-Service-Icons_04302026/Arch_Databases/32/Arch_Amazon-DynamoDB_32.png"
}


def get_icon(service, icon_root):
    filename = ICON_MAP.get(service)

    if not filename:
        return None

    return Path(icon_root) / filename
