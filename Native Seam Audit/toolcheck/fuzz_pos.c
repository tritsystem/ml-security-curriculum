#include <stdint.h>
#include <stddef.h>
#include <string.h>
/* planted seam bug: a length field trusted without checking the buffer size */
int LLVMFuzzerTestOneInput(const uint8_t *d, size_t n){
  if (n >= 4 && memcmp(d, "SEAM", 4) == 0 && n >= 5) {
    char buf[8]; size_t len = d[4];
    if (n >= 5 + len) memcpy(buf, d + 5, len);                           /* len up to 255 into buf[8] */
  }
  return 0; }
