#include <stdio.h>
#include <stdint.h>
#include <limits.h>
int main(int argc, char **argv){ volatile int a = INT_MAX; volatile uint32_t n = 0x40000000u;
  int s = a + argc;                         /* signed overflow */
  uint32_t bytes = n * 8u;                  /* size-math wrap: 2^30 * 8 -> 0 */
  printf("%d %u\n", s, bytes); return 0; }
