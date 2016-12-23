"""
Holds common file IO operations
"""
import os
import errno


def mkdirs(path):
    """
    Makes full directory path. Only throws exception if directory could not
    be created or already exists and is not a directory.
    :param str path: Absolute path to create.
    :raises OSError: When directory cannot be created or path exists but is not
        a directory.
    """
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            return
        raise OSError('Could not create dir %s: %s' % (path, e.message))
