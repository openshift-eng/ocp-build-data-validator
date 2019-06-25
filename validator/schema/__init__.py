from . import image_schema, rpm_schema
from .. import support


def validate(file, data):
    return {
        'image': image_schema.validate,
        'rpm': rpm_schema.validate,
    }.get(support.get_artifact_type(file), err)(file, data)


def err(*_):
    return ('Could not determine a schema\n'
            'Supported schemas: image, rpm\n'
            'Make sure the file is placed in either dir "images" or "rpms"')
