#!/usr/bin/env python3
"""Exercise the actual playback address gate with low/high native layer addresses.

This tests whether valid notes reach playback processing, not their audible output.
The pre-fix control must reproduce the skipped low-address note.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    source = (args.source/'mm/src/audio/lib/playback.c').read_text()
    start = source.index('        if (playbackState->parentLayer != NO_LAYER) {',
                         source.index('void AudioPlayback_ProcessNotes(void)'))
    end = source.index('            if ((note != playbackState->parentLayer->note)', start)
    gate = source[start:end] + '\n        }\n'
    program = r'''
#include <stdint.h>
#include <stdio.h>
#define NO_LAYER ((void*)(uintptr_t)-1)
struct Playback {void* parentLayer;};
static int reaches_processing(uintptr_t address) {
    struct Playback state={(void*)address}, *playbackState=&state;
    int processed=0;
    for(int i=0;i<1;i++) {
GATE
        processed++;
    }
    return processed;
}
int main(void) {
    uintptr_t addresses[]={0x00400000,0x02000000,0x7ffffffe,0x80000000,0x100000000,(uintptr_t)NO_LAYER};
    for(unsigned i=0;i<sizeof(addresses)/sizeof(addresses[0]);i++) {
        if(!reaches_processing(addresses[i])) {
            fprintf(stderr,"Skipped valid playback address: 0x%lx\n",(unsigned long)addresses[i]);
            return 1;
        }
    }
    puts("PASS: low/high native notes and NO_LAYER reach playback processing");
    return 0;
}
'''
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for name, block in [('fixed', gate), ('before', gate.replace(
                '#if !defined(__WIIU__) && !defined(__PROSPERO__)', '#ifndef __WIIU__'))]:
            if name == 'before' and block == gate:
                raise RuntimeError('Cannot construct pre-fix control')
            code=root/(name+'.c'); code.write_text(program.replace('GATE',block))
            binary=root/name
            subprocess.run(['clang','-D__PROSPERO__','-fsanitize=address,undefined',
                            str(code),'-o',str(binary)],check=True)
            result=subprocess.run([str(binary)],capture_output=True,text=True)
            if name=='fixed':
                if result.returncode:raise RuntimeError(result.stderr)
                print(result.stdout.strip())
            else:
                if result.returncode!=1 or 'Skipped valid playback address: 0x400000' not in result.stderr:
                    raise RuntimeError('Pre-fix control did not reproduce the missing-note bug')
                print('PASS: pre-fix control reproduces skipped low-address note')


if __name__=='__main__':
    main()
