from schema import Schema, Optional, And, SchemaError

STREAMS_SCHEMA = {
        And(str, len): {
            'image': And(str, len),
            'upstream_image_base': And(str, len),
            'upstream_image': And(str, len),
            Optional('mirror'): bool,
            Optional('transform'): And(str, len),
        },
    }


def streams_schema():
    return Schema(STREAMS_SCHEMA)


def validate(_, data):
    try:
        streams_schema().validate(data)
    except SchemaError as err:
        return '{}'.format(err)
