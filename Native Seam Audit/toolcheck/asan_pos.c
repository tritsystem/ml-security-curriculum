#include <stdlib.h>
int main(void){ char *p = malloc(8); p[8] = 1; free(p); return 0; }      /* 1-byte heap overflow */
