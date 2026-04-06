// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from helmholtz_interfaces:msg/Command.idl
// generated code does not contain a copyright notice

#ifndef HELMHOLTZ_INTERFACES__MSG__DETAIL__COMMAND__BUILDER_HPP_
#define HELMHOLTZ_INTERFACES__MSG__DETAIL__COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "helmholtz_interfaces/msg/detail/command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace helmholtz_interfaces
{

namespace msg
{

namespace builder
{

class Init_Command_z
{
public:
  explicit Init_Command_z(::helmholtz_interfaces::msg::Command & msg)
  : msg_(msg)
  {}
  ::helmholtz_interfaces::msg::Command z(::helmholtz_interfaces::msg::Command::_z_type arg)
  {
    msg_.z = std::move(arg);
    return std::move(msg_);
  }

private:
  ::helmholtz_interfaces::msg::Command msg_;
};

class Init_Command_y
{
public:
  explicit Init_Command_y(::helmholtz_interfaces::msg::Command & msg)
  : msg_(msg)
  {}
  Init_Command_z y(::helmholtz_interfaces::msg::Command::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_Command_z(msg_);
  }

private:
  ::helmholtz_interfaces::msg::Command msg_;
};

class Init_Command_x
{
public:
  explicit Init_Command_x(::helmholtz_interfaces::msg::Command & msg)
  : msg_(msg)
  {}
  Init_Command_y x(::helmholtz_interfaces::msg::Command::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_Command_y(msg_);
  }

private:
  ::helmholtz_interfaces::msg::Command msg_;
};

class Init_Command_type
{
public:
  Init_Command_type()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Command_x type(::helmholtz_interfaces::msg::Command::_type_type arg)
  {
    msg_.type = std::move(arg);
    return Init_Command_x(msg_);
  }

private:
  ::helmholtz_interfaces::msg::Command msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::helmholtz_interfaces::msg::Command>()
{
  return helmholtz_interfaces::msg::builder::Init_Command_type();
}

}  // namespace helmholtz_interfaces

#endif  // HELMHOLTZ_INTERFACES__MSG__DETAIL__COMMAND__BUILDER_HPP_
