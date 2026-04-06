// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from helmholtz_interfaces:srv/SetPID.idl
// generated code does not contain a copyright notice

#ifndef HELMHOLTZ_INTERFACES__SRV__DETAIL__SET_PID__STRUCT_H_
#define HELMHOLTZ_INTERFACES__SRV__DETAIL__SET_PID__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/SetPID in the package helmholtz_interfaces.
typedef struct helmholtz_interfaces__srv__SetPID_Request
{
  float kp;
  float ki;
  float kd;
} helmholtz_interfaces__srv__SetPID_Request;

// Struct for a sequence of helmholtz_interfaces__srv__SetPID_Request.
typedef struct helmholtz_interfaces__srv__SetPID_Request__Sequence
{
  helmholtz_interfaces__srv__SetPID_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} helmholtz_interfaces__srv__SetPID_Request__Sequence;


// Constants defined in the message

/// Struct defined in srv/SetPID in the package helmholtz_interfaces.
typedef struct helmholtz_interfaces__srv__SetPID_Response
{
  float kp_out;
  float ki_out;
  float kd_out;
  bool success;
} helmholtz_interfaces__srv__SetPID_Response;

// Struct for a sequence of helmholtz_interfaces__srv__SetPID_Response.
typedef struct helmholtz_interfaces__srv__SetPID_Response__Sequence
{
  helmholtz_interfaces__srv__SetPID_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} helmholtz_interfaces__srv__SetPID_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HELMHOLTZ_INTERFACES__SRV__DETAIL__SET_PID__STRUCT_H_
