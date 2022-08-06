# Generated Cmake Pico project file

cmake_minimum_required(VERSION 3.13)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialise pico_sdk from installed location
# (note this can come from environment, CMake cache etc)
# set(PICO_SDK_PATH "~/pico/pico-sdk")

# Pull in Raspberry Pi Pico SDK (must be before project)
include(pico_sdk_import.cmake)

project(utglitcher C CXX ASM)

# Initialise the Raspberry Pi Pico SDK
pico_sdk_init()

# Add executable. Default name is the project name, version 0.1

add_executable(utglitcher utglitcher.c )

pico_set_program_name(utglitcher "utglitcher")
pico_set_program_version(utglitcher "0.3")

pico_enable_stdio_uart(utglitcher 0)
pico_enable_stdio_usb(utglitcher 1)

# Add the standard library to the build
target_link_libraries(utglitcher pico_stdlib)

# Add any user requested libraries
target_link_libraries(utglitcher
        hardware_pio
        pico_multicore
        )

pico_generate_pio_header(utglitcher ${CMAKE_CURRENT_LIST_DIR}/pulsegen.pio)
pico_add_extra_outputs(utglitcher)
