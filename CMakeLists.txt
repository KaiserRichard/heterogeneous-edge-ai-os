cmake_minimum_required(VERSION 3.20)
project(heterogeneous_edge_ai_os C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# Enforce strict warning flags across all targets
if(CMAKE_C_COMPILER_ID MATCHES "Clang|AppleClang|GNU")
    add_compile_options(-Wall -Wextra -Werror -pedantic)
endif()

# -----------------------------------------------------------------------------
# 1. Protocol Core (Hardware- and transport-independent semantic encoding)
# -----------------------------------------------------------------------------
add_library(protocol STATIC
    protocol/src/protocol.c
)
target_include_directories(protocol PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/protocol/include
)

# -----------------------------------------------------------------------------
# 2. Supervisor State Machine (Portable C core for STM32 supervisor)
# -----------------------------------------------------------------------------
add_library(supervisor STATIC
    stm32/src/supervisor.c
)
target_include_directories(supervisor PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/stm32/include
)

# -----------------------------------------------------------------------------
# 3. Linux Workload Library (Timing abstraction and synthetic compute)
# -----------------------------------------------------------------------------
add_library(workload STATIC
    linux/src/timing.c
    linux/src/workload.c
)
target_include_directories(workload PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/linux/include
)

# -----------------------------------------------------------------------------
# 4. Linux Workload Runner Executable
# -----------------------------------------------------------------------------
add_executable(workload_runner
    linux/src/main.c
)
target_link_libraries(workload_runner PRIVATE workload)

# -----------------------------------------------------------------------------
# 5. Unit Tests
# -----------------------------------------------------------------------------
enable_testing()

add_executable(test_protocol tests/test_protocol.c)
target_link_libraries(test_protocol PRIVATE protocol)
target_include_directories(test_protocol PRIVATE tests)
add_test(NAME test_protocol COMMAND test_protocol)

add_executable(test_supervisor tests/test_supervisor.c)
target_link_libraries(test_supervisor PRIVATE supervisor)
target_include_directories(test_supervisor PRIVATE tests)
add_test(NAME test_supervisor COMMAND test_supervisor)

add_executable(test_workload tests/test_workload.c)
target_link_libraries(test_workload PRIVATE workload)
target_include_directories(test_workload PRIVATE tests)
add_test(NAME test_workload COMMAND test_workload)
