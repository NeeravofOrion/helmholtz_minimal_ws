// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from helmholtz_interfaces:srv/SetPID.idl
// generated code does not contain a copyright notice
#include "helmholtz_interfaces/srv/detail/set_pid__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

bool
helmholtz_interfaces__srv__SetPID_Request__init(helmholtz_interfaces__srv__SetPID_Request * msg)
{
  if (!msg) {
    return false;
  }
  // kp
  // ki
  // kd
  return true;
}

void
helmholtz_interfaces__srv__SetPID_Request__fini(helmholtz_interfaces__srv__SetPID_Request * msg)
{
  if (!msg) {
    return;
  }
  // kp
  // ki
  // kd
}

bool
helmholtz_interfaces__srv__SetPID_Request__are_equal(const helmholtz_interfaces__srv__SetPID_Request * lhs, const helmholtz_interfaces__srv__SetPID_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // kp
  if (lhs->kp != rhs->kp) {
    return false;
  }
  // ki
  if (lhs->ki != rhs->ki) {
    return false;
  }
  // kd
  if (lhs->kd != rhs->kd) {
    return false;
  }
  return true;
}

bool
helmholtz_interfaces__srv__SetPID_Request__copy(
  const helmholtz_interfaces__srv__SetPID_Request * input,
  helmholtz_interfaces__srv__SetPID_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // kp
  output->kp = input->kp;
  // ki
  output->ki = input->ki;
  // kd
  output->kd = input->kd;
  return true;
}

helmholtz_interfaces__srv__SetPID_Request *
helmholtz_interfaces__srv__SetPID_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  helmholtz_interfaces__srv__SetPID_Request * msg = (helmholtz_interfaces__srv__SetPID_Request *)allocator.allocate(sizeof(helmholtz_interfaces__srv__SetPID_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(helmholtz_interfaces__srv__SetPID_Request));
  bool success = helmholtz_interfaces__srv__SetPID_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
helmholtz_interfaces__srv__SetPID_Request__destroy(helmholtz_interfaces__srv__SetPID_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    helmholtz_interfaces__srv__SetPID_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
helmholtz_interfaces__srv__SetPID_Request__Sequence__init(helmholtz_interfaces__srv__SetPID_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  helmholtz_interfaces__srv__SetPID_Request * data = NULL;

  if (size) {
    data = (helmholtz_interfaces__srv__SetPID_Request *)allocator.zero_allocate(size, sizeof(helmholtz_interfaces__srv__SetPID_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = helmholtz_interfaces__srv__SetPID_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        helmholtz_interfaces__srv__SetPID_Request__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
helmholtz_interfaces__srv__SetPID_Request__Sequence__fini(helmholtz_interfaces__srv__SetPID_Request__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      helmholtz_interfaces__srv__SetPID_Request__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

helmholtz_interfaces__srv__SetPID_Request__Sequence *
helmholtz_interfaces__srv__SetPID_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  helmholtz_interfaces__srv__SetPID_Request__Sequence * array = (helmholtz_interfaces__srv__SetPID_Request__Sequence *)allocator.allocate(sizeof(helmholtz_interfaces__srv__SetPID_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = helmholtz_interfaces__srv__SetPID_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
helmholtz_interfaces__srv__SetPID_Request__Sequence__destroy(helmholtz_interfaces__srv__SetPID_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    helmholtz_interfaces__srv__SetPID_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
helmholtz_interfaces__srv__SetPID_Request__Sequence__are_equal(const helmholtz_interfaces__srv__SetPID_Request__Sequence * lhs, const helmholtz_interfaces__srv__SetPID_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!helmholtz_interfaces__srv__SetPID_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
helmholtz_interfaces__srv__SetPID_Request__Sequence__copy(
  const helmholtz_interfaces__srv__SetPID_Request__Sequence * input,
  helmholtz_interfaces__srv__SetPID_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(helmholtz_interfaces__srv__SetPID_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    helmholtz_interfaces__srv__SetPID_Request * data =
      (helmholtz_interfaces__srv__SetPID_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!helmholtz_interfaces__srv__SetPID_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          helmholtz_interfaces__srv__SetPID_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!helmholtz_interfaces__srv__SetPID_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


bool
helmholtz_interfaces__srv__SetPID_Response__init(helmholtz_interfaces__srv__SetPID_Response * msg)
{
  if (!msg) {
    return false;
  }
  // kp_out
  // ki_out
  // kd_out
  // success
  return true;
}

void
helmholtz_interfaces__srv__SetPID_Response__fini(helmholtz_interfaces__srv__SetPID_Response * msg)
{
  if (!msg) {
    return;
  }
  // kp_out
  // ki_out
  // kd_out
  // success
}

bool
helmholtz_interfaces__srv__SetPID_Response__are_equal(const helmholtz_interfaces__srv__SetPID_Response * lhs, const helmholtz_interfaces__srv__SetPID_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // kp_out
  if (lhs->kp_out != rhs->kp_out) {
    return false;
  }
  // ki_out
  if (lhs->ki_out != rhs->ki_out) {
    return false;
  }
  // kd_out
  if (lhs->kd_out != rhs->kd_out) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  return true;
}

bool
helmholtz_interfaces__srv__SetPID_Response__copy(
  const helmholtz_interfaces__srv__SetPID_Response * input,
  helmholtz_interfaces__srv__SetPID_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // kp_out
  output->kp_out = input->kp_out;
  // ki_out
  output->ki_out = input->ki_out;
  // kd_out
  output->kd_out = input->kd_out;
  // success
  output->success = input->success;
  return true;
}

helmholtz_interfaces__srv__SetPID_Response *
helmholtz_interfaces__srv__SetPID_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  helmholtz_interfaces__srv__SetPID_Response * msg = (helmholtz_interfaces__srv__SetPID_Response *)allocator.allocate(sizeof(helmholtz_interfaces__srv__SetPID_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(helmholtz_interfaces__srv__SetPID_Response));
  bool success = helmholtz_interfaces__srv__SetPID_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
helmholtz_interfaces__srv__SetPID_Response__destroy(helmholtz_interfaces__srv__SetPID_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    helmholtz_interfaces__srv__SetPID_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
helmholtz_interfaces__srv__SetPID_Response__Sequence__init(helmholtz_interfaces__srv__SetPID_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  helmholtz_interfaces__srv__SetPID_Response * data = NULL;

  if (size) {
    data = (helmholtz_interfaces__srv__SetPID_Response *)allocator.zero_allocate(size, sizeof(helmholtz_interfaces__srv__SetPID_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = helmholtz_interfaces__srv__SetPID_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        helmholtz_interfaces__srv__SetPID_Response__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
helmholtz_interfaces__srv__SetPID_Response__Sequence__fini(helmholtz_interfaces__srv__SetPID_Response__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      helmholtz_interfaces__srv__SetPID_Response__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

helmholtz_interfaces__srv__SetPID_Response__Sequence *
helmholtz_interfaces__srv__SetPID_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  helmholtz_interfaces__srv__SetPID_Response__Sequence * array = (helmholtz_interfaces__srv__SetPID_Response__Sequence *)allocator.allocate(sizeof(helmholtz_interfaces__srv__SetPID_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = helmholtz_interfaces__srv__SetPID_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
helmholtz_interfaces__srv__SetPID_Response__Sequence__destroy(helmholtz_interfaces__srv__SetPID_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    helmholtz_interfaces__srv__SetPID_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
helmholtz_interfaces__srv__SetPID_Response__Sequence__are_equal(const helmholtz_interfaces__srv__SetPID_Response__Sequence * lhs, const helmholtz_interfaces__srv__SetPID_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!helmholtz_interfaces__srv__SetPID_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
helmholtz_interfaces__srv__SetPID_Response__Sequence__copy(
  const helmholtz_interfaces__srv__SetPID_Response__Sequence * input,
  helmholtz_interfaces__srv__SetPID_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(helmholtz_interfaces__srv__SetPID_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    helmholtz_interfaces__srv__SetPID_Response * data =
      (helmholtz_interfaces__srv__SetPID_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!helmholtz_interfaces__srv__SetPID_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          helmholtz_interfaces__srv__SetPID_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!helmholtz_interfaces__srv__SetPID_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
