add_library(usermod_duo75 INTERFACE)

get_filename_component(REPO_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../" ABSOLUTE)

target_sources(usermod_duo75 INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/duo75.c
    ${CMAKE_CURRENT_LIST_DIR}/duo75.cpp
    ${REPO_ROOT}/drivers/duo75/duo75.cpp
)

target_include_directories(usermod_${MOD_NAME} INTERFACE
    ${REPO_ROOT}
    ${PIMORONI_PICO_PATH}
    ${CMAKE_CURRENT_LIST_DIR}
    ${PIMORONI_PICO_PATH}/libraries/pico_graphics/
)

target_compile_definitions(usermod_${MOD_NAME} INTERFACE
    MODULE_HUB75_ENABLED=1
)

set_source_files_properties(
    ${CMAKE_CURRENT_LIST_DIR}/duo75.c
    PROPERTIES COMPILE_FLAGS
    "-Wno-discarded-qualifiers -Wno-implicit-int"
)

pico_generate_pio_header(usermod_duo75 ${REPO_ROOT}/drivers/duo75/duo75.pio)

set_source_files_properties(${REPO_ROOT}/drivers/duo75/duo75.cpp PROPERTIES COMPILE_OPTIONS "-O2;-fgcse-after-reload;-floop-interchange;-fpeel-loops;-fpredictive-commoning;-fsplit-paths;-ftree-loop-distribute-patterns;-ftree-loop-distribution;-ftree-vectorize;-ftree-partial-pre;-funswitch-loops")

target_link_libraries(usermod INTERFACE usermod_duo75)