cmake_minimum_required(VERSION 3.5.1)
project(chirc C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_BUILD_TYPE Debug)

include_directories(src lib/uthash/include lib/sds)

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
target_link_libraries(chirc pthread)

set(ASSIGNMENTS
    1 2 3 4 5 2+3 2+3+5 4+5)

foreach(AID ${ASSIGNMENTS})

    add_custom_target(categories-assignment-${AID}
            COMMAND ../tests/print-categories.py ../tests/rubrics/assignment-${AID}.json)

    # Plus sign found, split the assignment ID into parts
    string(REPLACE "+" ";" ASSIGN_LIST ${AID})

    # Generate a string of rubrics to pass to the command
    set(RUBRIC_ARGS "")
    set(PYTEST_ARGS "")
    foreach(ID IN LISTS ASSIGN_LIST)
        list(APPEND RUBRIC_ARGS ../tests/rubrics/assignment-${ID}.json)
        list(APPEND PYTEST_ARGS --chirc-rubric ../tests/rubrics/assignment-${ID}.json)
    endforeach()

    add_custom_target(tests-assignment-${AID}
            COMMAND pytest ${PYTEST_ARGS} ../tests/
            DEPENDS chirc)

    add_custom_target(assignment-${AID}
            COMMAND /bin/sh -c 'pytest ${PYTEST_ARGS} ../tests/\; exit 0'
            COMMAND ../tests/grade.py ${RUBRIC_ARGS}
            DEPENDS chirc)

    add_custom_target(grade-assignment-${AID}
            COMMAND ../tests/grade.py ${RUBRIC_ARGS})

endforeach()

