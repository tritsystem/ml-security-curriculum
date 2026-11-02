// Planted GPU seam bugs, one per compute-sanitizer tool; mode 0 = clean negative control.
#include <cstdio>
#include <cuda_runtime.h>
__global__ void oob(int *a, int n){ int i = blockIdx.x*blockDim.x + threadIdx.x; if (i <= n) a[i] = i; }   // <= : writes a[n]
__global__ void ok(int *a, int n){ int i = blockIdx.x*blockDim.x + threadIdx.x; if (i < n) a[i] = i; }
__global__ void uninit(const int *src, int *dst){ dst[threadIdx.x] = src[threadIdx.x] + 1; }              // src never written
__global__ void race(int *out){ __shared__ int s; s = threadIdx.x; out[threadIdx.x] = s; }                  // shared-mem hazard
__global__ void badsync(int *out){ __shared__ int s[64]; s[threadIdx.x] = threadIdx.x;
  if (threadIdx.x < 16) __syncthreads();                                                                    // divergent barrier
  out[threadIdx.x] = s[63 - threadIdx.x]; }
__global__ void badwarp(int *out){ __syncwarp(0x0000FFFFu); out[threadIdx.x] = threadIdx.x; }   // lanes 16-31 not in mask
int main(int argc, char **argv){
  int mode = argc > 1 ? atoi(argv[1]) : 0, n = 64, *a, *b;
  cudaMalloc(&a, n*sizeof(int)); cudaMalloc(&b, n*sizeof(int));
  if (mode == 0) { cudaMemset(a, 0, n*sizeof(int)); ok<<<1,64>>>(a, n); }
  if (mode == 1) oob<<<1,128>>>(a, n);
  if (mode == 2) uninit<<<1,64>>>(a, b);
  if (mode == 3) race<<<1,64>>>(a);
  if (mode == 4) badsync<<<1,64>>>(a);
  if (mode == 5) badwarp<<<1,32>>>(a);
  cudaError_t e = cudaDeviceSynchronize(); printf("mode %d: %s\n", mode, cudaGetErrorString(e));
  cudaFree(a); cudaFree(b); return 0; }

