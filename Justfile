build:
    make all

clean:
    make clean

test:
    make test

check:
    cppcheck --enable=warning,performance,portability,information --suppress=missingIncludeSystem -I include -I src src
    # clang-tidy src/*.c -- -Iinclude -Isrc -std=c11
