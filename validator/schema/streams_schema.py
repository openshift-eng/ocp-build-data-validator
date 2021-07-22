from schema import Schema, Optional, And, SchemaError


def streams_schema(file):
    return Schema({
        And(str, len): {
            'image': And(str, len),
            'upstream_image_base': And(str, len),
            'upstream_image': And(str, len),
            Optional('mirror'): bool,
            Optional('transform'): And(str, len),
        },
    })


def validate(file, data):
    try:
        streams_schema(file).validate(data)
    except SchemaError as err:
        return '{}'.format(err)
