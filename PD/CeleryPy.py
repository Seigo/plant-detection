#!/usr/bin/env python
"""Celery Py.

Python wrappers for FarmBot Celery Script JSON nodes.
"""
import os
import json
from functools import wraps


def _print_json(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        """Send Celery Script or return the JSON string.

        Celery Script is sent by prefixing the string in the `BEGIN_CS`
        environment variable.
        """
        try:
            begin_cs = os.environ['BEGIN_CS']
        except KeyError:
            return function(*args, **kwargs)
        else:
            print(begin_cs + json.dumps(function(*args, **kwargs)))
            return
    return wrapper


def _encode_coordinates(x_coord, y_coord, z_coord):
    coords = {}
    coords['x'] = x_coord
    coords['y'] = y_coord
    coords['z'] = z_coord
    return coords


def create_node(kind=None, args=None):
    """Create a kind, args Celery Script node."""
    node = {}
    node['kind'] = kind
    node['args'] = args
    return node


def create_pair(label=None, value=None):
    """Create a label, value Celery Script node."""
    pair = {}
    pair['label'] = label
    pair['value'] = value
    return pair


def _saved_location_node(name, _id):
    args = {}
    args[name + '_id'] = _id
    saved_location = create_node(kind=name, args=args)
    return saved_location


def _coordinate_node(x_coord, y_coord, z_coord):
    coordinates = _encode_coordinates(x_coord, y_coord, z_coord)
    coordinate = create_node(kind='coordinate', args=coordinates)
    return coordinate


@_print_json
def add_point(point_x, point_y, point_z, point_r):
    """Celery Script to add a point to the database.

    Kind:
        add_point
    Arguments:
        Location:
            Coordinate (x, y, z)
        Radius: r
    Body:
        Kind: pair
        Args:
            label: created_by
            value: plant-detection
    """
    args = {}
    args['location'] = _coordinate_node(point_x, point_y, point_z)
    args['radius'] = point_r
    point = create_node(kind='add_point', args=args)
    created_by = create_pair(label='created_by', value='plant-detection')
    point['body'] = [create_node(kind='pair', args=created_by)]
    return point


@_print_json
def set_user_env(label, value):
    """Celery Script to set an environment variable.

    Kind:
        set_user_env
    Body:
        Kind: pair
        Args:
            label: <ENV VAR name>
            value: <ENV VAR value>
    """
    _set_user_env = create_node(kind='set_user_env', args={})
    env_var = create_pair(label=label, value=value)
    _set_user_env['body'] = [create_node(kind='pair', args=env_var)]
    return _set_user_env


@_print_json
def move_absolute(location, offset, speed):
    """Celery Script to move to a location.

    Kind:
        move_absolute
    Arguments:
        Location:
            Coordinate (x, y, z) or Saved Location ['tool', tool_id]
        Offset:
            Distance (x, y, z)
        Speed:
            Speed (mm/s)
    """
    args = {}
    if len(location) == 2:
        args['location'] = _saved_location_node(
            location[0], location[1])
    if len(location) == 3:
        args['location'] = _coordinate_node(*location)
    args['offset'] = _coordinate_node(*offset)
    args['speed'] = speed
    _move_absolute = create_node(kind='move_absolute', args=args)
    return _move_absolute


@_print_json
def move_relative(distance=(0, 0, 0), speed=800):
    """Celery Script to move relative to the current location.

    Kind:
        move_relative
    Arguments:
        x distance (mm)
        y distance (mm)
        z distance (mm)
        Speed (mm/s)
    """
    args = _encode_coordinates(*distance)
    args['speed'] = speed
    _move_relative = create_node(kind='move_relative', args=args)
    return _move_relative


@_print_json
def data_update(endpoint, ids_):
    """Celery Script to signal that a sync is required.

    Kind:
        data_update
    Args:
        value: updated
    Body:
        Kind: pair
        Args:
            label: endpoint
            value: id
    """
    args = {}
    args['value'] = 'updated'
    _data_update = create_node(kind='data_update', args=args)
    if isinstance(ids_, list):
        body = []
        for id_ in ids_:
            _endpoint = create_pair(label=endpoint, value=str(id_))
            body.append(create_node(kind='pair', args=_endpoint))
    else:
        _endpoint = create_pair(label=endpoint, value=ids_)
        body = [create_node(kind='pair', args=_endpoint)]
    _data_update['body'] = body
    return _data_update


@_print_json
def send_message(message='Hello World!', message_type='success', channel=None):
    """Celery Script to send a message.

    Kind:
        send_message
    Arguments:
        message
        message_type: success, busy, warn, error, info, fun
        channel: toast
    """
    args = {}
    args['message'] = message
    args['message_type'] = message_type
    _send_message = create_node(kind='send_message', args=args)
    if channel is not None:
        body = [create_node(kind='channel', args={"channel_name": channel})]
        _send_message['body'] = body
    return _send_message


@_print_json
def if_statement(lhs='x', op='is', rhs=0, _then=None, _else=None):
    """Celery Script if statement.

    Kind:
        _if
    Arguments:
        lhs (left-hand side)
        op (operator)
        rhs (right-hand side)
        _then (id of sequence to execute on `then`)
        _else (id of sequence to execute on `else`)
    """
    args = {}
    args['lhs'] = lhs
    args['op'] = op
    args['rhs'] = rhs
    if _then is None:
        _then_args = {}
    else:
        _then_args = {"sequence_id": _then}
    if _else is None:
        _else_args = {}
    else:
        _else_args = {"sequence_id": _else}
    args['_then'] = create_node(kind='nothing', args=_then_args)
    args['_else'] = create_node(kind='nothing', args=_else_args)
    _if_statement = create_node(kind='_if', args=args)
    return _if_statement


@_print_json
def write_pin(number=0, value=0, mode=0):
    """Celery Script to write a value to a pin.

    Kind:
        write_pin
    Arguments:
        pin_number: 0
        pin_value: 0 [0, 1]
        pin_mode: 0 [0, 1]
    """
    args = {}
    args['pin_number'] = number
    args['pin_value'] = value
    args['pin_mode'] = mode
    _write_pin = create_node(kind='write_pin', args=args)
    return _write_pin


@_print_json
def read_pin(number=0, mode=0, label='---'):
    """Celery Script to read the value of a pin.

    Kind:
        read_pin
    Arguments:
        pin_number: 0
        pin_mode: 0 [0, 1]
        label: '---'
    """
    args = {}
    args['pin_number'] = number
    args['pin_mode'] = mode
    args['label'] = label
    _read_pin = create_node(kind='read_pin', args=args)
    return _read_pin


@_print_json
def execute_sequence(sequence_id=0):
    """Celery Script to execute a sequence.

    Kind:
        execute
    Arguments:
        sequence_id: 0
    """
    args = {}
    args['sequence_id'] = sequence_id
    _execute_sequence = create_node(kind='execute', args=args)
    return _execute_sequence


@_print_json
def execute_script(label):
    """Celery Script to execute a farmware.

    Kind:
        execute_script
    Arguments:
        label
    """
    args = {}
    args['label'] = label
    _execute_script = create_node(kind='execute_script', args=args)
    return _execute_script


@_print_json
def take_photo():
    """Celery Script to take a photo.

    Kind:
        take_photo
    Arguments:
        {}
    """
    args = {}
    _take_photo = create_node(kind='take_photo', args=args)
    return _take_photo


@_print_json
def wait(milliseconds=0):
    """Celery Script to wait.

    Kind:
        wait
    Arguments:
        milliseconds: 0
    """
    args = {}
    args['milliseconds'] = milliseconds
    _wait = create_node(kind='wait', args=args)
    return _wait
