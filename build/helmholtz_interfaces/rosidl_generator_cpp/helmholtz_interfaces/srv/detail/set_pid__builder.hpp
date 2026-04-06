// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from helmholtz_interfaces:srv/SetPID.idl
// generated code does not contain a copyright notice

#ifndef HELMHOLTZ_INTERFACES__SRV__DETAIL__SET_PID__BUILDER_HPP_
#define HELMHOLTZ_INTERFACES__SRV__DETAIL__SET_PID__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "helmholtz_interfaces/srv/detail/set_pid__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace helmholtz_interfaces
{

namespace srv
{

namespace builder
{

class Init_SetPID_Request_kd
{
public:
  explicit Init_SetPID_Request_kd(::helmholtz_interfaces::srv::SetPID_Request & msg)
  : msg_(msg)
  {}
  ::helmholtz_interfaces::srv::SetPID_Request kd(::helmholtz_interfaces::srv::SetPID_Request::_kd_type arg)
  {
    msg_.kd = std::move(arg);
    return std::move(msg_);
  }

private:
  ::helmholtz_interfaces::srv::SetPID_Request msg_;
};

class Init_SetPID_Request_ki
{
public:
  explicit Init_SetPID_Request_ki(::helmholtz_interfaces::srv::SetPID_Request & msg)
  : msg_(msg)
  {}
  Init_SetPID_Request_kd ki(::helmholtz_interfaces::srv::SetPID_Request::_ki_type arg)
  {
    msg_.ki = std::move(arg);
    return Init_SetPID_Request_kd(msg_);
  }

private:
  ::helmholtz_interfaces::srv::SetPID_Request msg_;
};

class Init_SetPID_Request_kp
{
public:
  Init_SetPID_Request_kp()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SetPID_Request_ki kp(::helmholtz_interfaces::srv::SetPID_Request::_kp_type arg)
  {
    msg_.kp = std::move(arg);
    return Init_SetPID_Request_ki(msg_);
  }

private:
  ::helmholtz_interfaces::srv::SetPID_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::helmholtz_interfaces::srv::SetPID_Request>()
{
  return helmholtz_interfaces::srv::builder::Init_SetPID_Request_kp();
}

}  // namespace helmholtz_interfaces


namespace helmholtz_interfaces
{

namespace srv
{

namespace builder
{

class Init_SetPID_Response_success
{
public:
  explicit Init_SetPID_Response_success(::helmholtz_interfaces::srv::SetPID_Response & msg)
  : msg_(msg)
  {}
  ::helmholtz_interfaces::srv::SetPID_Response success(::helmholtz_interfaces::srv::SetPID_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return std::move(msg_);
  }

private:
  ::helmholtz_interfaces::srv::SetPID_Response msg_;
};

class Init_SetPID_Response_kd_out
{
public:
  explicit Init_SetPID_Response_kd_out(::helmholtz_interfaces::srv::SetPID_Response & msg)
  : msg_(msg)
  {}
  Init_SetPID_Response_success kd_out(::helmholtz_interfaces::srv::SetPID_Response::_kd_out_type arg)
  {
    msg_.kd_out = std::move(arg);
    return Init_SetPID_Response_success(msg_);
  }

private:
  ::helmholtz_interfaces::srv::SetPID_Response msg_;
};

class Init_SetPID_Response_ki_out
{
public:
  explicit Init_SetPID_Response_ki_out(::helmholtz_interfaces::srv::SetPID_Response & msg)
  : msg_(msg)
  {}
  Init_SetPID_Response_kd_out ki_out(::helmholtz_interfaces::srv::SetPID_Response::_ki_out_type arg)
  {
    msg_.ki_out = std::move(arg);
    return Init_SetPID_Response_kd_out(msg_);
  }

private:
  ::helmholtz_interfaces::srv::SetPID_Response msg_;
};

class Init_SetPID_Response_kp_out
{
public:
  Init_SetPID_Response_kp_out()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SetPID_Response_ki_out kp_out(::helmholtz_interfaces::srv::SetPID_Response::_kp_out_type arg)
  {
    msg_.kp_out = std::move(arg);
    return Init_SetPID_Response_ki_out(msg_);
  }

private:
  ::helmholtz_interfaces::srv::SetPID_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::helmholtz_interfaces::srv::SetPID_Response>()
{
  return helmholtz_interfaces::srv::builder::Init_SetPID_Response_kp_out();
}

}  // namespace helmholtz_interfaces

#endif  // HELMHOLTZ_INTERFACES__SRV__DETAIL__SET_PID__BUILDER_HPP_
