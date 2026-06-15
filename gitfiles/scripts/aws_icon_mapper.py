# aws_icon_mapper.py

from aws_icon_registry import AwsIconRegistry

_registry = None


def get_icon(service, icon_root):

    global _registry

    if _registry is None:
        _registry = AwsIconRegistry(icon_root)

    return _registry.get_icon(service)