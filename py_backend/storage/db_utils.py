import sqlalchemy


def object_as_dict(obj):
    """Converts a SQLAlchemy object into a dictionary."""
    return {
        c.key: getattr(obj, c.key) for c in sqlalchemy.inspect(obj).mapper.column_attrs
    }
