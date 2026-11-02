#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
static int g; static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
static void *w(void *a){ for (int i=0;i<100000;i++){ pthread_mutex_lock(&m); g++; pthread_mutex_unlock(&m);} return 0; }
int main(int argc, char **argv){
  char *p = malloc(8); memset(p, 0, 8); p[7] = 1;                        /* in bounds, initialized */
  int x = argc; if (x > 0) puts("ok");
  uint64_t bytes = (uint64_t)0x40000000u * 8u;                            /* widened: no wrap */
  pthread_t t1,t2; pthread_create(&t1,0,w,0); pthread_create(&t2,0,w,0); pthread_join(t1,0); pthread_join(t2,0);
  printf("%d %llu %d\n", g, (unsigned long long)bytes, p[7]); free(p); return 0; }
