CXX ?= c++
CC ?= cc
PYTHON ?= python3
CPPFLAGS += -D_GNU_SOURCE -D_DEFAULT_SOURCE -D_DARWIN_C_SOURCE -D_POSIX_C_SOURCE=200809L -I../include
CXXFLAGS ?= -std=c++17 -O2 -g -Wall -Wextra -Wpedantic -Werror
CFLAGS ?= -std=c99 -O2 -g -Wall -Wextra -Wpedantic -Werror
HAVE_LIBCAMERA := $(shell pkg-config --exists libcamera 2>/dev/null && echo yes)
ifeq ($(HAVE_LIBCAMERA),yes)
CAM_SRC := libcamera_backend.cpp
CAM_FLAGS := $(shell pkg-config --cflags libcamera) -DHEA_HAVE_LIBCAMERA
CAM_LIBS := $(shell pkg-config --libs libcamera)
else
$(info libcamera unavailable via pkg-config: skipping real backend; building fake backend)
endif
ifeq ($(shell uname -s),Darwin)
SHARED := -dynamiclib
LIB := build/libhea_camera.dylib
else
SHARED := -shared
LIB := build/libhea_camera.so
CAM_LIBS += -lrt
endif
.PHONY: all test clean
all: build/hea_cam $(LIB)
build:
	mkdir -p $@
build/hea_runtime.o: ../src/hea_runtime.c ../include/hea_runtime.h | build
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@
build/hea_ipc.o: ../src/hea_ipc.c ../include/hea_ipc.h | build
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@
build/hea_cam: hea_cam.cpp ring.cpp ring.h camera.h $(CAM_SRC) build/hea_runtime.o build/hea_ipc.o
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(CAM_FLAGS) hea_cam.cpp ring.cpp $(CAM_SRC) build/hea_runtime.o build/hea_ipc.o $(LDFLAGS) $(CAM_LIBS) -pthread -o $@
$(LIB): ring.cpp ring.h | build
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -fPIC $(SHARED) ring.cpp $(LDFLAGS) -o $@
build/test_ring: tests/test_ring.cpp ring.cpp ring.h | build
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -DHEA_CAMERA_TEST_HOOK -fsanitize=address,undefined -I. tests/test_ring.cpp ring.cpp -pthread -o $@
test: all build/test_ring
	./build/test_ring
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -v
clean:
	rm -rf build
