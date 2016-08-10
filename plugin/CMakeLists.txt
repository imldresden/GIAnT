cmake_minimum_required(VERSION 2.8.4)
project(plots)
include(CheckCXXCompilerFlag)

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
                "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support.")
        endif()
    endif()
endfunction(set_cxx_version)

set(SOURCE_FILES plots_wrapper.cpp VWLineNode.cpp ScatterPlotNode.cpp HeadData.cpp User.cpp Path.cpp)
set(CMAKE_SHARED_MODULE_PREFIX)
add_library(plots MODULE ${SOURCE_FILES})

execute_process(COMMAND python -c "import os;import libavg;print os.path.dirname(libavg.__file__)"
        OUTPUT_VARIABLE AVG_LIB_PATH OUTPUT_STRIP_TRAILING_WHITESPACE)

include_directories("/usr/local/include/libavg/")
if (NOT APPLE)
    target_link_libraries(plots ${AVG_LIB_PATH}/avg.so)
endif()

find_package(PythonLibs REQUIRED)
include_directories("${PYTHON_INCLUDE_DIRS}")
target_link_libraries(plots ${PYTHON_LIBRARIES})

if (APPLE)
    target_link_libraries(plots -bundle -flat_namespace "-undefined suppress")
    execute_process(COMMAND xml2-config --cflags OUTPUT_VARIABLE LIBXML2_CFLAGS)
    add_definitions(${LIBXML2_CFLAGS})
    set(CMAKE_MODULE_LINKER_FLAGS "-undefined dynamic_lookup ${CMAKE_MODULE_LINKER_FLAGS} -lxml2")
else()
    find_package(LibXml2 REQUIRED)
    include_directories("${LIBXML2_INCLUDE_DIR}")
    target_link_libraries(plots ${LIBXML2_LIBRARIES})
endif()
set_cxx_version()

FIND_PACKAGE(Boost REQUIRED)
INCLUDE_DIRECTORIES("${Boost_INCLUDE_DIRS}" "${PYTHON_INCLUDE_DIRS}")
SET(Boost_USE_STATIC_LIBS OFF)
SET(Boost_USE_MULTITHREADED ON)
SET(Boost_USE_STATIC_RUNTIME OFF)
FIND_PACKAGE(Boost COMPONENTS python system)
TARGET_LINK_LIBRARIES(plots ${Boost_LIBRARIES})

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wno-invalid-offsetof -Woverloaded-virtual -Wswitch -Wuninitialized -Wempty-body -Wno-unused-local-typedefs")
install(TARGETS plots LIBRARY DESTINATION ${AVG_LIB_PATH}/plugin)

if (APPLE)
    add_custom_target(run_install COMMAND osascript -e
            "do shell script \\\"make install\\\" with administrator privileges")
else ()
    add_custom_target(run_install COMMAND sudo -A ${CMAKE_MAKE_PROGRAM} install)
endif()
