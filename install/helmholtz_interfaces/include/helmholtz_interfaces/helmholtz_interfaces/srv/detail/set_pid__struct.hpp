// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from helmholtz_interfaces:srv/SetPID.idl
// generated code does not contain a copyright notice

#ifndef HELMHOLTZ_INTERFACES__SRV__DETAIL__SET_PID__STRUCT_HPP_
#define HELMHOLTZ_INTERFACES__SRV__DETAIL__SET_PID__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__helmholtz_interfaces__srv__SetPID_Request __attribute__((deprecated))
#else
# define DEPRECATED__helmholtz_interfaces__srv__SetPID_Request __declspec(deprecated)
#endif

namespace helmholtz_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct SetPID_Request_
{
  using Type = SetPID_Request_<ContainerAllocator>;

  explicit SetPID_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->kp = 0.0f;
      this->ki = 0.0f;
      this->kd = 0.0f;
    }
  }

  explicit SetPID_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->kp = 0.0f;
      this->ki = 0.0f;
      this->kd = 0.0f;
    }
  }

  // field types and members
  using _kp_type =
    float;
  _kp_type kp;
  using _ki_type =
    float;
  _ki_type ki;
  using _kd_type =
    float;
  _kd_type kd;

  // setters for named parameter idiom
  Type & set__kp(
    const float & _arg)
  {
    this->kp = _arg;
    return *this;
  }
  Type & set__ki(
    const float & _arg)
  {
    this->ki = _arg;
    return *this;
  }
  Type & set__kd(
    const float & _arg)
  {
    this->kd = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    helmholtz_interfaces::srv::SetPID_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const helmholtz_interfaces::srv::SetPID_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<helmholtz_interfaces::srv::SetPID_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<helmholtz_interfaces::srv::SetPID_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      helmholtz_interfaces::srv::SetPID_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<helmholtz_interfaces::srv::SetPID_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      helmholtz_interfaces::srv::SetPID_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<helmholtz_interfaces::srv::SetPID_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<helmholtz_interfaces::srv::SetPID_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<helmholtz_interfaces::srv::SetPID_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__helmholtz_interfaces__srv__SetPID_Request
    std::shared_ptr<helmholtz_interfaces::srv::SetPID_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__helmholtz_interfaces__srv__SetPID_Request
    std::shared_ptr<helmholtz_interfaces::srv::SetPID_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SetPID_Request_ & other) const
  {
    if (this->kp != other.kp) {
      return false;
    }
    if (this->ki != other.ki) {
      return false;
    }
    if (this->kd != other.kd) {
      return false;
    }
    return true;
  }
  bool operator!=(const SetPID_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SetPID_Request_

// alias to use template instance with default allocator
using SetPID_Request =
  helmholtz_interfaces::srv::SetPID_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace helmholtz_interfaces


#ifndef _WIN32
# define DEPRECATED__helmholtz_interfaces__srv__SetPID_Response __attribute__((deprecated))
#else
# define DEPRECATED__helmholtz_interfaces__srv__SetPID_Response __declspec(deprecated)
#endif

namespace helmholtz_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct SetPID_Response_
{
  using Type = SetPID_Response_<ContainerAllocator>;

  explicit SetPID_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->kp_out = 0.0f;
      this->ki_out = 0.0f;
      this->kd_out = 0.0f;
      this->success = false;
    }
  }

  explicit SetPID_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->kp_out = 0.0f;
      this->ki_out = 0.0f;
      this->kd_out = 0.0f;
      this->success = false;
    }
  }

  // field types and members
  using _kp_out_type =
    float;
  _kp_out_type kp_out;
  using _ki_out_type =
    float;
  _ki_out_type ki_out;
  using _kd_out_type =
    float;
  _kd_out_type kd_out;
  using _success_type =
    bool;
  _success_type success;

  // setters for named parameter idiom
  Type & set__kp_out(
    const float & _arg)
  {
    this->kp_out = _arg;
    return *this;
  }
  Type & set__ki_out(
    const float & _arg)
  {
    this->ki_out = _arg;
    return *this;
  }
  Type & set__kd_out(
    const float & _arg)
  {
    this->kd_out = _arg;
    return *this;
  }
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    helmholtz_interfaces::srv::SetPID_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const helmholtz_interfaces::srv::SetPID_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<helmholtz_interfaces::srv::SetPID_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<helmholtz_interfaces::srv::SetPID_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      helmholtz_interfaces::srv::SetPID_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<helmholtz_interfaces::srv::SetPID_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      helmholtz_interfaces::srv::SetPID_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<helmholtz_interfaces::srv::SetPID_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<helmholtz_interfaces::srv::SetPID_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<helmholtz_interfaces::srv::SetPID_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__helmholtz_interfaces__srv__SetPID_Response
    std::shared_ptr<helmholtz_interfaces::srv::SetPID_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__helmholtz_interfaces__srv__SetPID_Response
    std::shared_ptr<helmholtz_interfaces::srv::SetPID_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SetPID_Response_ & other) const
  {
    if (this->kp_out != other.kp_out) {
      return false;
    }
    if (this->ki_out != other.ki_out) {
      return false;
    }
    if (this->kd_out != other.kd_out) {
      return false;
    }
    if (this->success != other.success) {
      return false;
    }
    return true;
  }
  bool operator!=(const SetPID_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SetPID_Response_

// alias to use template instance with default allocator
using SetPID_Response =
  helmholtz_interfaces::srv::SetPID_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace helmholtz_interfaces

namespace helmholtz_interfaces
{

namespace srv
{

struct SetPID
{
  using Request = helmholtz_interfaces::srv::SetPID_Request;
  using Response = helmholtz_interfaces::srv::SetPID_Response;
};

}  // namespace srv

}  // namespace helmholtz_interfaces

#endif  // HELMHOLTZ_INTERFACES__SRV__DETAIL__SET_PID__STRUCT_HPP_
