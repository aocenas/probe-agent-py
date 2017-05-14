import functools
import inspect


def get_name(event, frame, arg):
    co = frame.f_code
    func_name = co.co_name

    if event == 'call':
        obj = _get_callable_object(frame)
    else:
        obj = arg

    return _get_full_name(obj) if obj else func_name


def _get_callable_object(frame):
    """
    Get and original callable object. Frame does not contain it directly so we have to search for it in globals.
    """

    co = frame.f_code
    func_name = co.co_name

    if func_name in frame.f_globals:
        try:
            if frame.f_globals[func_name].__code__ is co:
                # free function
                return frame.f_globals[func_name]
        except Exception:
            pass

    for name, obj in frame.f_globals.items():
        try:
            if obj.__dict__[func_name].__code__ is co:
                # a method of an object
                return obj.__dict__[func_name]
        except Exception:
            pass

    return None


def _get_full_name(object):

    # partial wrappers
    if isinstance(object, functools.partial):
        object = object.func

    owner = None

    if inspect.ismethod(object):
        # class method, __self__ is a class
        class_name = getattr(object.__self__, '__qualname__', None)
        owner = object.__self__

        if class_name is None:
            # instance method, __self__ is an object of some class
            class_name = getattr(object.__self__.__class__, '__qualname__')
            owner = object.__self__.__class__

        path = '%s.%s' % (class_name, object.__name__)

    else:
        path = getattr(object, '__qualname__', None)
        # type object
        if path is None and hasattr(object, '__class__'):
            path = getattr(object.__class__, '__qualname__')

    module_name = _get_module_name(owner or object)
    return ':'.join([module_name, path])


def _get_module_name(object):
    module_name = None

    if hasattr(object, '__objclass__'):
        module_name = getattr(object.__objclass__, '__module__', None)

    # standard way
    if module_name is None:
        module_name = getattr(object, '__module__', None)

    # builtins or C code
    if module_name is None:
        self = getattr(object, '__self__', None)
        if self is not None and hasattr(self, '__class__'):
            module_name = getattr(self.__class__, '__module__', None)

    if module_name is None and hasattr(object, '__class__'):
        module_name = getattr(object.__class__, '__module__', None)

    return module_name or 'unknown'
