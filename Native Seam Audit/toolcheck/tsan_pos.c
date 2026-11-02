#include <pthread.h>
#include <stdio.h>
int g; void *w(void *a){ for (int i=0;i<100000;i++) g++; return 0; }    /* unsynchronized shared write */
int main(void){ pthread_t t1,t2; pthread_create(&t1,0,w,0); pthread_create(&t2,0,w,0);
  pthread_join(t1,0); pthread_join(t2,0); printf("%d\n", g); return 0; }
