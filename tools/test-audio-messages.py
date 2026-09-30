#!/usr/bin/env python3
"""Exercise the game's audio message receivers with AddressSanitizer on a 64-bit host.

Run with the patched 2Ship source directory. Compiles the actual receiver bodies and
libultraship queue implementation so narrowed receive buffers fail under ASan.
"""
import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile


def function(source, name):
    match = re.search(r"^\w+ " + re.escape(name) + r"\([^;]*?\) \{", source, re.M)
    if match is None:
        raise ValueError(f"Function definition not found: {name}")
    start = match.start()
    opening = source.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end] + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--cc", default="clang")
    args = parser.parse_args()
    root = args.source
    load = (root / "mm/src/audio/lib/load.c").read_text()
    thread = (root / "mm/src/audio/lib/thread.c").read_text()
    queue = (root / "libultraship/src/libultraship/libultra/os_mesg.cpp").read_text()
    header = (root / "libultraship/include/libultraship/libultra/message.h").read_text()
    harness = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stddef.h>
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef int8_t s8;
typedef int32_t s32;
typedef struct OSThread OSThread;
'''
    harness += header.replace('#include "thread.h"', '')
    harness += r'''
_Static_assert(sizeof(OSMesg) == 8, "Regression requires a 64-bit host");
typedef struct { u8* sampleAddr; u32 size; u8 medium; } Sample;
typedef struct {
    Sample* sample;
    u8* ramAddr;
    u32 encodedInfo;
    bool isFree;
    u32 endAndMediumKey;
} AudioPreloadReq;
enum { MEDIUM_RAM = 0 };
static struct {
    OSMesgQueue externalLoadQueue, preloadSampleQueue;
    OSMesgQueue* audioResetQueueP;
    AudioPreloadReq preloadSampleStack[16];
    s32 preloadSampleStackTop;
} gAudioCtx;
static OSMesgQueue sScriptLoadQueue;
static s8* sScriptLoadDonePointers[16];
static unsigned starts;
static void AudioLoad_StartAsyncLoad(uintptr_t src, u8* dst, u32 size, u8 medium,
                                    u32 chunks, OSMesgQueue* queue, u32 info) {
    starts++;
}
'''
    for name in ("osCreateMesgQueue", "osSendMesg", "osRecvMesg"):
        harness += function(queue, name)
    for name in ("AudioLoad_ProcessScriptLoads", "AudioLoad_ProcessSamplePreloads"):
        harness += function(load, name)
    for name in ("AudioThread_GetExternalLoadQueueMsg", "AudioThread_WaitForAudioResetQueueP"):
        harness += function(thread, name)
    harness += r'''
int main(void) {
    OSMesg script[16], external[16], preload[16], reset[16];
    OSMesgQueue resetQueue;
    s8 done[16];
    u32 result;
    osCreateMesgQueue(&sScriptLoadQueue, script, 16);
    osCreateMesgQueue(&gAudioCtx.externalLoadQueue, external, 16);
    osCreateMesgQueue(&gAudioCtx.preloadSampleQueue, preload, 16);
    osCreateMesgQueue(&resetQueue, reset, 16);
    gAudioCtx.audioResetQueueP = &resetQueue;
    for (int i = 0; i < 16; ++i) {
        done[i] = -1;
        sScriptLoadDonePointers[i] = &done[i];
        assert(osSendMesg32(&sScriptLoadQueue, ((u32)i << 24) | 0x123456, 0) == 0);
    }
    for (int i = 0; i < 16; ++i) {
        AudioLoad_ProcessScriptLoads();
        assert(done[i] == 0);
        if (i < 15) assert(done[i + 1] == -1);
    }
    AudioLoad_ProcessScriptLoads();
    sScriptLoadDonePointers[3] = NULL;
    osSendMesg32(&sScriptLoadQueue, 3u << 24, 0);
    AudioLoad_ProcessScriptLoads();
    assert(AudioThread_GetExternalLoadQueueMsg(&result) == 0 && result == 0);
    osSendMesg32(&gAudioCtx.externalLoadQueue, 0xa5123456u, 0);
    assert(AudioThread_GetExternalLoadQueueMsg(&result) == 0xa5 && result == 0x123456);
    for (int i = 0; i < 16; ++i) osSendMesg8(&resetQueue, i, 0);
    AudioThread_WaitForAudioResetQueueP();
    assert(resetQueue.validCount == 0);
    AudioThread_WaitForAudioResetQueueP();
    u8 original[16], loaded[16];
    Sample sample = { original, sizeof(original), 2 };
    for (int i = 0; i < 16; ++i) {
        AudioPreloadReq* req = &gAudioCtx.preloadSampleStack[i];
        req->isFree = true;
    }
    AudioPreloadReq* req = &gAudioCtx.preloadSampleStack[7];
    *req = (AudioPreloadReq){ &sample, loaded, 7u << 24, false,
                             (u32)((uintptr_t)original + sizeof(original) + 2) };
    gAudioCtx.preloadSampleStackTop = 8;
    assert(!AudioLoad_ProcessSamplePreloads(0));
    osSendMesg32(&gAudioCtx.preloadSampleQueue, (7u << 24) | 0xffffff, 0);
    assert(AudioLoad_ProcessSamplePreloads(0));
    assert(sample.sampleAddr == loaded && sample.medium == MEDIUM_RAM);
    assert(req->isFree && gAudioCtx.preloadSampleStackTop == 0 && starts == 0);
    gAudioCtx.preloadSampleStackTop = 1;
    osSendMesg32(&gAudioCtx.preloadSampleQueue, 0xffffff, 0);
    assert(!AudioLoad_ProcessSamplePreloads(1));
    assert(gAudioCtx.preloadSampleStackTop == 0 && gAudioCtx.preloadSampleQueue.validCount == 0);
    puts("PASS: script completion, external load, reset drain, sample preload (64-bit ASan)");
}
'''
    with tempfile.TemporaryDirectory(prefix="audio-messages-") as temp:
        source = Path(temp) / "test.c"
        binary = Path(temp) / "test"
        source.write_text(harness)
        subprocess.run([args.cc, "-std=c11", "-O1", "-g", "-fsanitize=address,undefined",
                        "-fno-omit-frame-pointer", str(source), "-o", str(binary)], check=True)
        env = dict(os.environ, ASAN_OPTIONS="detect_leaks=0")
        subprocess.run([str(binary)], check=True, env=env)


if __name__ == "__main__":
    main()
