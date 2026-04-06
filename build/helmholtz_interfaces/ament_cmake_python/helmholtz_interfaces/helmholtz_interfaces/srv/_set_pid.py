# generated from rosidl_generator_py/resource/_idl.py.em
# with input from helmholtz_interfaces:srv/SetPID.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_SetPID_Request(type):
    """Metaclass of message 'SetPID_Request'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('helmholtz_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'helmholtz_interfaces.srv.SetPID_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__set_pid__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__set_pid__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__set_pid__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__set_pid__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__set_pid__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class SetPID_Request(metaclass=Metaclass_SetPID_Request):
    """Message class 'SetPID_Request'."""

    __slots__ = [
        '_kp',
        '_ki',
        '_kd',
    ]

    _fields_and_field_types = {
        'kp': 'float',
        'ki': 'float',
        'kd': 'float',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.kp = kwargs.get('kp', float())
        self.ki = kwargs.get('ki', float())
        self.kd = kwargs.get('kd', float())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.kp != other.kp:
            return False
        if self.ki != other.ki:
            return False
        if self.kd != other.kd:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def kp(self):
        """Message field 'kp'."""
        return self._kp

    @kp.setter
    def kp(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'kp' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'kp' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._kp = value

    @builtins.property
    def ki(self):
        """Message field 'ki'."""
        return self._ki

    @ki.setter
    def ki(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'ki' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'ki' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._ki = value

    @builtins.property
    def kd(self):
        """Message field 'kd'."""
        return self._kd

    @kd.setter
    def kd(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'kd' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'kd' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._kd = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import math

# already imported above
# import rosidl_parser.definition


class Metaclass_SetPID_Response(type):
    """Metaclass of message 'SetPID_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('helmholtz_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'helmholtz_interfaces.srv.SetPID_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__set_pid__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__set_pid__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__set_pid__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__set_pid__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__set_pid__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class SetPID_Response(metaclass=Metaclass_SetPID_Response):
    """Message class 'SetPID_Response'."""

    __slots__ = [
        '_kp_out',
        '_ki_out',
        '_kd_out',
        '_success',
    ]

    _fields_and_field_types = {
        'kp_out': 'float',
        'ki_out': 'float',
        'kd_out': 'float',
        'success': 'boolean',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.kp_out = kwargs.get('kp_out', float())
        self.ki_out = kwargs.get('ki_out', float())
        self.kd_out = kwargs.get('kd_out', float())
        self.success = kwargs.get('success', bool())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.kp_out != other.kp_out:
            return False
        if self.ki_out != other.ki_out:
            return False
        if self.kd_out != other.kd_out:
            return False
        if self.success != other.success:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def kp_out(self):
        """Message field 'kp_out'."""
        return self._kp_out

    @kp_out.setter
    def kp_out(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'kp_out' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'kp_out' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._kp_out = value

    @builtins.property
    def ki_out(self):
        """Message field 'ki_out'."""
        return self._ki_out

    @ki_out.setter
    def ki_out(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'ki_out' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'ki_out' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._ki_out = value

    @builtins.property
    def kd_out(self):
        """Message field 'kd_out'."""
        return self._kd_out

    @kd_out.setter
    def kd_out(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'kd_out' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'kd_out' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._kd_out = value

    @builtins.property
    def success(self):
        """Message field 'success'."""
        return self._success

    @success.setter
    def success(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'success' field must be of type 'bool'"
        self._success = value


class Metaclass_SetPID(type):
    """Metaclass of service 'SetPID'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('helmholtz_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'helmholtz_interfaces.srv.SetPID')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__set_pid

            from helmholtz_interfaces.srv import _set_pid
            if _set_pid.Metaclass_SetPID_Request._TYPE_SUPPORT is None:
                _set_pid.Metaclass_SetPID_Request.__import_type_support__()
            if _set_pid.Metaclass_SetPID_Response._TYPE_SUPPORT is None:
                _set_pid.Metaclass_SetPID_Response.__import_type_support__()


class SetPID(metaclass=Metaclass_SetPID):
    from helmholtz_interfaces.srv._set_pid import SetPID_Request as Request
    from helmholtz_interfaces.srv._set_pid import SetPID_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
