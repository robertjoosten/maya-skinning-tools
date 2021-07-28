import sys
from six.moves import range
from maya import mel


def as_mel_procedure(func, arguments=(), return_type=None):
    """
    Create a mel procedure that will call the provided function.
    This mel procedure can then be used to in contexts etc.

    :param func:
    :param list[tuple] arguments:
    :param str return_type:
    :return: Procedure name
    :rtype: str
    """
    # create python look up
    procedure = "__{}".format("_".join([func.__name__, str(id(func))]))
    sys.modules["__main__"].__dict__[procedure] = func

    # create mel procedure
    mel_arguments_string = ",".join(["{} ${}".format(type_name, name) for type_name, name in arguments])
    python_arguments_string = ",".join(['\'"+${}+"\''.format(name) for _, name in arguments])

    mel.eval(
        'global proc {1} {0}({3}){{{2} python("{0}({4})");}}'.format(
            procedure,
            return_type or "",
            "return" if return_type is not None else "",
            mel_arguments_string,
            python_arguments_string,
        )
    )

    return procedure


def as_chunks(l, num):
    """
    :param list l:
    :param int num: Size of split
    :return: Split list
    :rtype: list
    """
    chunks = []
    for i in range(0, len(l), num):
        chunks.append(l[i:i + num])
    return chunks


def normalize(l):
    """
    :param list[float] l:
    :return: Normalized values
    :rtype: list[float]
    """
    multiplier = 1.0 / sum(l)
    return [value * multiplier for value in l]