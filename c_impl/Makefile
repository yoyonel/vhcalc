CC = gcc
CFLAGS = -std=c11 -O3 -Wall -Wextra -Wpedantic -Wstrict-prototypes -Wshadow -Iinclude -Isrc -Itests
LDFLAGS = -lm
PREFIX = /usr/local
BINDIR = $(PREFIX)/bin

SRC = src/main.c src/imghash.c src/video_reader.c
OBJ = src/main.o src/imghash.o src/video_reader.o
TARGET = build/vhcalc
TEST_SRC = tests/test_imghash.c
TEST_OBJ = tests/test_imghash.o
TEST_TARGET = build/test_vhcalc

.PHONY: all clean test install uninstall asan

all: $(TARGET)

$(TARGET): $(OBJ)
	mkdir -p build
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJ) $(TARGET) $(TEST_OBJ) $(TEST_TARGET)
	rm -rf build

test: $(TEST_TARGET)
	./$(TEST_TARGET)

$(TEST_TARGET): $(TEST_OBJ)
	mkdir -p build
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

install: all
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 $(TARGET) $(DESTDIR)$(BINDIR)/vhcalc

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/vhcalc

asan: CFLAGS += -fsanitize=address -g
asan: LDFLAGS += -fsanitize=address
asan: clean all test
