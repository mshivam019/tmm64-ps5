#!/usr/bin/env python3
"""Exercise the actual synthesis chunk calculation with exhausted/reused notes."""
from pathlib import Path
import subprocess,tempfile,sys
root=Path(sys.argv[1])
s=(root/'mm/src/audio/lib/synthesis.c').read_text()
a=s.index('                numFirstFrameSamplesToIgnore = synthState->samplePosInt & 0xF;')
b=s.index('                // Set parameters based on compression type',a)
chunk=s[a:b]
prefix='''#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
typedef int s32;
#define SAMPLES_PER_FRAME 16
static int run(int position,int endpoint,int count,int requested,int *processed) {
 struct {int samplePosInt;bool atLoopPoint,stopLoop;} state={position,false,false},*synthState=&state;
 struct {int count;} loop={count},*loopInfo=&loop;
 int sampleEndPos=endpoint,numSamplesToLoadAdj=requested,numSamplesProcessed=0;
 int numFirstFrameSamplesToIgnore,numSamplesUntilEnd,numSamplesToProcess,numSamplesInFirstFrame;
 int numFramesToDecode,numSamplesToDecode,numTrailingSamplesToIgnore;
 bool sampleFinished=false,loopToPoint=false;
'''
suffix='''
 *processed=numSamplesToDecode+numSamplesInFirstFrame-numTrailingSamplesToIgnore;
 assert(numFramesToDecode>=0 && numSamplesToDecode>=0 && *processed>=0 && *processed<=requested);
 return numSamplesToDecode;
}
int main(void){
 int p;
 run(30772,27693,1,160,&p);assert(p==0); /* stale cursor: original produces negative progress */
 run(27693,27693,1,160,&p);assert(p==0);
 run(9682,27693,1,160,&p);assert(p==160); /* recorded loop restart */
 run(27683,27693,0,160,&p);assert(p==10);
 for(int position=0;position<28000;position+=7)
  for(int n=1;n<=400;n+=13)run(position,27693,1,n,&p);
 puts("audio sample-end regression passed");
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(prefix+chunk+suffix)
 subprocess.run(['clang','-fsanitize=address,undefined','-g',str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
 # Verify regression really detects pre-fix negative progress.
 old=chunk.replace('''                if (numSamplesUntilEnd < 0) {
                    numSamplesUntilEnd = 0;
                }''','')
 assert old!=chunk
 (p/'test.c').write_text(prefix+old+suffix)
 subprocess.run(['clang',str(p/'test.c'),'-o',str(p/'old')],check=True)
 r=subprocess.run([str(p/'old')],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 assert r.returncode!=0
 print('Pre-fix calculation fails the same regression as expected')
