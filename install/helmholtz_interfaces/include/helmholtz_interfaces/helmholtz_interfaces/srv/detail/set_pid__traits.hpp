// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from helmholtz_interfaces:srv/SetPID.idl
// generated code does not contain a copyright notice

#ifndef HELMHOLTZ_INTERFACES__SRV__DETAIL__SET_PID__TRAITS_HPP_
#define HELMHOLTZ_INTERFACES__SRV__DETAIL__SET_PID__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "helmholtz_interfaces/srv/detail/set_pid__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace helmholtz_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const SetPID_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: kp
  {
    out << "kp: ";
    rosidl_generator_traits::value_to_yaml(msg.kp, out);
    out << ", ";
  }

  // member: ki
  {
    out << "ki: ";
    rosidl_generator_traits::value_to_yaml(msg.ki, out);
    out << ", ";
  }

  // member: kd
  {
    out << "kd: ";
    rosidl_generator_traits::value_to_yaml(msg.kd, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SetPID_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: kp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "kp: ";
    rosidl_generator_traits::value_to_yaml(msg.kp, out);
    out << "\n";
  }

  // member: ki
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "ki: ";
    rosidl_generator_traits::value_to_yaml(msg.ki, out);
    out << "\n";
  }

  // member: kd
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "kd: ";
    rosidl_generator_traits::value_to_yaml(msg.kd, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SetPID_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace helmholtz_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use helmholtz_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const helmholtz_interfaces::srv::SetPID_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  helmholtz_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use helmholtz_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const helmholtz_interfaces::srv::SetPID_Request & msg)
{
  return helmholtz_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<helmholtz_interfaces::srv::SetPID_Request>()
{
  return "helmholtz_interfaces::srv::SetPID_Request";
}

template<>
inline const char * name<helmholtz_interfaces::srv::SetPID_Request>()
{
  return "helmholtz_interfaces/srv/SetPID_Request";
}

template<>
struct has_fixed_size<helmholtz_interfaces::srv::SetPID_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<helmholtz_interfaces::srv::SetPID_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<helmholtz_interfaces::srv::SetPID_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace helmholtz_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const SetPID_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: kp_out
  {
    out << "kp_out: ";
    rosidl_generator_traits::value_to_yaml(msg.kp_out, out);
    out << ", ";
  }

  // member: ki_out
  {
    out << "ki_out: ";
    rosidl_generator_traits::value_to_yaml(msg.ki_out, out);
    out << ", ";
  }

  // member: kd_out
  {
    out << "kd_out: ";
    rosidl_generator_traits::value_to_yaml(msg.kd_out, out);
    out << ", ";
  }

  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SetPID_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: kp_out
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "kp_out: ";
    rosidl_generator_traits::value_to_yaml(msg.kp_out, out);
    out << "\n";
  }

  // member: ki_out
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "ki_out: ";
    rosidl_generator_traits::value_to_yaml(msg.ki_out, out);
    out << "\n";
  }

  // member: kd_out
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "kd_out: ";
    rosidl_generator_traits::value_to_yaml(msg.kd_out, out);
    out << "\n";
  }

  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SetPID_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace helmholtz_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use helmholtz_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const helmholtz_interfaces::srv::SetPID_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  helmholtz_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use helmholtz_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const helmholtz_interfaces::srv::SetPID_Response & msg)
{
  return helmholtz_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<helmholtz_interfaces::srv::SetPID_Response>()
{
  return "helmholtz_interfaces::srv::SetPID_Response";
}

template<>
inline const char * name<helmholtz_interfaces::srv::SetPID_Response>()
{
  return "helmholtz_interfaces/srv/SetPID_Response";
}

template<>
struct has_fixed_size<helmholtz_interfaces::srv::SetPID_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<helmholtz_interfaces::srv::SetPID_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<helmholtz_interfaces::srv::SetPID_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<helmholtz_interfaces::srv::SetPID>()
{
  return "helmholtz_interfaces::srv::SetPID";
}

template<>
inline const char * name<helmholtz_interfaces::srv::SetPID>()
{
  return "helmholtz_interfaces/srv/SetPID";
}

template<>
struct has_fixed_size<helmholtz_interfaces::srv::SetPID>
  : std::integral_constant<
    bool,
    has_fixed_size<helmholtz_interfaces::srv::SetPID_Request>::value &&
    has_fixed_size<helmholtz_interfaces::srv::SetPID_Response>::value
  >
{
};

template<>
struct has_bounded_size<helmholtz_interfaces::srv::SetPID>
  : std::integral_constant<
    bool,
    has_bounded_size<helmholtz_interfaces::srv::SetPID_Request>::value &&
    has_bounded_size<helmholtz_interfaces::srv::SetPID_Response>::value
  >
{
};

template<>
struct is_service<helmholtz_interfaces::srv::SetPID>
  : std::true_type
{
};

template<>
struct is_service_request<helmholtz_interfaces::srv::SetPID_Request>
  : std::true_type
{
};

template<>
struct is_service_response<helmholtz_interfaces::srv::SetPID_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // HELMHOLTZ_INTERFACES__SRV__DETAIL__SET_PID__TRAITS_HPP_
