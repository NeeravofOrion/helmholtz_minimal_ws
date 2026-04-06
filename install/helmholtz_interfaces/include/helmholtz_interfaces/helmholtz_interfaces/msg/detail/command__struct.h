// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from helmholtz_interfaces:msg/Command.idl
// generated code does not contain a copyright notice

#ifndef HELMHOLTZ_INTERFACES__MSG__DETAIL__COMMAND__STRUCT_H_
#define HELMHOLTZ_INTERFACES__MSG__DETAIL__COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Command in the package helmholtz_interfaces.
typedef struct helmholtz_interfaces__msg__Command
{
  uint8_t type;
  float x;
  float y;
  float z;
} helmholtz_interfaces__msg__Command;

// Struct for a sequence of helmholtz_interfaces__msg__Command.
typedef struct helmholtz_interfaces__msg__Command__Sequence
{
  helmholtz_interfaces__msg__Command * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} helmholtz_interfaces__msg__Command__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HELMHOLTZ_INTERFACES__MSG__DETAIL__COMMAND__STRUCT_H_
