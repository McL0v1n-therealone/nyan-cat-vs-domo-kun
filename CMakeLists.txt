cmake_minimum_required(VERSION 3.5)
project(nyancat C)
add_executable(nyancat main.c)
target_compile_options(nyancat PRIVATE -O2 -Wall)
target_link_libraries(nyancat pspdebug pspdisplay pspge pspctrl pspaudio psppower m)
create_pbp_file(
    TARGET nyancat
    TITLE "Nyan Cat vs Domo-kun"
    ICON_PATH ${CMAKE_SOURCE_DIR}/assets/ICON0.PNG
    BACKGROUND_PATH ${CMAKE_SOURCE_DIR}/assets/PIC1.PNG
)
