#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "helmholtz_interfaces::helmholtz_interfaces__rosidl_typesupport_c" for configuration ""
set_property(TARGET helmholtz_interfaces::helmholtz_interfaces__rosidl_typesupport_c APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(helmholtz_interfaces::helmholtz_interfaces__rosidl_typesupport_c PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_NOCONFIG "rosidl_runtime_c::rosidl_runtime_c;rosidl_typesupport_c::rosidl_typesupport_c"
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libhelmholtz_interfaces__rosidl_typesupport_c.so"
  IMPORTED_SONAME_NOCONFIG "libhelmholtz_interfaces__rosidl_typesupport_c.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS helmholtz_interfaces::helmholtz_interfaces__rosidl_typesupport_c )
list(APPEND _IMPORT_CHECK_FILES_FOR_helmholtz_interfaces::helmholtz_interfaces__rosidl_typesupport_c "${_IMPORT_PREFIX}/lib/libhelmholtz_interfaces__rosidl_typesupport_c.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
