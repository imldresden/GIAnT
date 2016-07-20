cmake_minimum_required(VERSION 2.8.4)
project(vwline)

function(set_cxx_version)
    check_cxx_compiler_flag("-std=c++11" COMPILER_SUPPORTS_CXX11)
    if(COMPILER_SUPPORTS_CXX11)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11" PARENT_SCOPE)
    else()
        check_cxx_compiler_flag("-std=c++0x" COMPILER_SUPPORTS_CXX0X)
        if(COMPILER_SUPPORTS_CXX0X)
            set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x" PARENT_SCOPE)
        else()
            message(FATAL_ERROR
                "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support. Please use a different C++ compiler.")
        endif()
    endif()
endfunction(set_cxx_version)

set(SOURCE_FILES vwline_wrapper.cpp VWLineNode.cpp)
set(CMAKE_SHARED_MODULE_PREFIX)
add_library(vwline MODULE ${SOURCE_FILES})

execute_process(COMMAND python -c "import os;import libavg;print os.path.dirname(libavg.__file__)"
        OUTPUT_VARIABLE AVG_LIB_PATH OUTPUT_STRIP_TRAILING_WHITESPACE)

include_directories("/usr/local/include/libavg/")
if (NOT APPLE)
    target_link_libraries(vwline ${AVG_LIB_PATH}/avg.so)
endif()

find_package(PythonLibs REQUIRED)
include_directories("${PYTHON_INCLUDE_DIRS}")
target_link_libraries(vwline ${PYTHON_LIBRARIES})

if (APPLE)
    execute_process(COMMAND xml2-config --cflags OUTPUT_VARIABLE LIBXML2_CFLAGS)
    add_definitions(${LIBXML2_CFLAGS})
    set(CMAKE_MODULE_LINKER_FLAGS "-undefined dynamic_lookup ${CMAKE_MODULE_LINKER_FLAGS} -lxml2")
else()
    find_package(LibXml2 REQUIRED)
    include_directories("${LIBXML2_INCLUDE_DIR}")
    target_link_libraries(vwline ${LIBXML2_LIBRARIES})
endif()

FIND_PACKAGE(Boost REQUIRED)
INCLUDE_DIRECTORIES("${Boost_INCLUDE_DIRS}" "${PYTHON_INCLUDE_DIRS}")
SET(Boost_USE_STATIC_LIBS OFF)
SET(Boost_USE_MULTITHREADED ON)
SET(Boost_USE_STATIC_RUNTIME OFF)
FIND_PACKAGE(Boost COMPONENTS python system)
TARGET_LINK_LIBRARIES(vwline ${Boost_LIBRARIES})

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Woverloaded-virtual -Wswitch -Wuninitialized -Wempty-body -Wno-unused-local-typedefs")

install(TARGETS vwline LIBRARY DESTINATION ${AVG_LIB_PATH}/plugin)

if (APPLE)
    add_custom_target(run_install COMMAND osascript -e
            "do shell script \\\"make install\\\" with administrator privileges")
else ()
    add_custom_target(run_install COMMAND sudo -A ${CMAKE_MAKE_PROGRAM} install)
endif()
