#!/usr/sbin/nbdkit python

API_VERSION = 2
SIZE = 1024 * 1024
STORE = bytes(SIZE)


class Handle:
    id = 0


def open(readonly) -> Handle:
    return Handle()


def get_size(h) -> int:
    return SIZE


def pread(h, buf, offset, flags) -> bytes:
    return STORE[offset:offset + len(buf)]
