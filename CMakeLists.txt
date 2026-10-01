cmake_minimum_required(VERSION 3.21)
project(chirc C)

# Default to a Debug build, but let -DCMAKE_BUILD_TYPE=... override it
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Debug CACHE STRING "Build type" FORCE)
endif()

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
# The code uses POSIX/GNU APIs (pthreads, getaddrinfo, NI_MAXHOST, ...)
# without feature-test macros, so it requires gnu17 rather than strict c17
set(CMAKE_C_EXTENSIONS ON)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

add_executable(chirc
        src/channel.c
        src/channeluser.c
        src/connection.c
        src/ctx.c
        src/handlers.c
        src/log.c
        src/main.c
        src/message.c
        src/server.c
        src/user.c
        src/utils.c
        lib/sds/sds.c)
target_include_directories(chirc PRIVATE src lib/uthash/include lib/sds)
target_compile_options(chirc PRIVATE -Wall -Wextra -Wno-unused-parameter)
target_link_libraries(chirc PRIVATE Threads::Threads)

set(TESTS_DIR ${PROJECT_SOURCE_DIR}/tests)

set(ASSIGNMENTS
    1 2 3 4 5 2+3 2+3+5 4+5)

foreach(AID ${ASSIGNMENTS})

    add_custom_target(categories-assignment-${AID}
            COMMAND ${TESTS_DIR}/print-categories.py ${TESTS_DIR}/rubrics/assignment-${AID}.json)

    # Plus sign found, split the assignment ID into parts
    string(REPLACE "+" ";" ASSIGN_LIST ${AID})

    # Generate a string of rubrics to pass to the command
    set(RUBRIC_ARGS "")
    set(PYTEST_ARGS --chirc-exe=$<TARGET_FILE:chirc>)
    foreach(ID IN LISTS ASSIGN_LIST)
        list(APPEND RUBRIC_ARGS ${TESTS_DIR}/rubrics/assignment-${ID}.json)
        list(APPEND PYTEST_ARGS --chirc-rubric ${TESTS_DIR}/rubrics/assignment-${ID}.json)
    endforeach()

    add_custom_target(tests-assignment-${AID}
            COMMAND pytest ${PYTEST_ARGS} ${TESTS_DIR}
            DEPENDS chirc)

    add_custom_target(assignment-${AID}
            COMMAND /bin/sh -c 'pytest ${PYTEST_ARGS} ${TESTS_DIR}\; exit 0'
            COMMAND ${TESTS_DIR}/grade.py ${RUBRIC_ARGS}
            DEPENDS chirc)

    add_custom_target(grade-assignment-${AID}
            COMMAND ${TESTS_DIR}/grade.py ${RUBRIC_ARGS})

endforeach()
