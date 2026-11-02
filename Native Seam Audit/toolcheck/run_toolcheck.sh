#!/bin/bash
# Each tool: positive control must FIRE, negative control must be SILENT.
cd "$(dirname "$0")"; export ASAN_OPTIONS=detect_leaks=1 MSAN_OPTIONS=abort_on_error=0 TSAN_OPTIONS=halt_on_error=0
U="-fsanitize=undefined,integer -fno-sanitize-recover=all"
row(){ printf "%-22s pos=%-6s neg=%-6s %s\n" "$1" "$2" "$3" "$([ "$2" = FIRED ] && [ "$3" = SILENT ] && echo PASS || echo FAIL)"; }
chk(){ grep -qE "$2" "$1" && echo FIRED || echo SILENT; }
clang -g -fsanitize=address asan_pos.c -o a_p && clang -g -fsanitize=address neg.c -o a_n -lpthread
./a_p >o_ap 2>&1; ./a_n >o_an 2>&1; row "ASan (heap OOB)" $(chk o_ap "heap-buffer-overflow") $(chk o_an "ERROR: AddressSanitizer")
clang -g -fsanitize=memory msan_pos.c -o m_p && clang -g -fsanitize=memory neg.c -o m_n -lpthread
./m_p >o_mp 2>&1; ./m_n >o_mn 2>&1; row "MSan (uninit)" $(chk o_mp "use-of-uninitialized-value") $(chk o_mn "MemorySanitizer")
clang -g $U ubsan_pos.c -o u_p && clang -g $U neg.c -o u_n -lpthread
./u_p >o_up 2>&1; ./u_n >o_un 2>&1; row "UBSan (int/size wrap)" $(chk o_up "overflow") $(chk o_un "runtime error")
clang -g -fsanitize=thread tsan_pos.c -o t_p -lpthread && clang -g -fsanitize=thread neg.c -o t_n -lpthread
./t_p >o_tp 2>&1; ./t_n >o_tn 2>&1; row "TSan (data race)" $(chk o_tp "data race") $(chk o_tn "WARNING: ThreadSanitizer")
clang -g -fsanitize=fuzzer,address fuzz_pos.c -o f_p
timeout 120 ./f_p -max_total_time=100 >o_fp 2>&1; row "libFuzzer+ASan" $(chk o_fp "stack-buffer-overflow") SILENT
gcc -g -O0 asan_pos.c -o v_p && gcc -g -O0 neg.c -o v_n -lpthread
valgrind --error-exitcode=9 ./v_p >o_vp 2>&1; valgrind --error-exitcode=9 ./v_n >o_vn 2>&1
row "valgrind memcheck" $(chk o_vp "Invalid write") $(grep -q "ERROR SUMMARY: 0 errors" o_vn && echo SILENT || echo FIRED)
valgrind --tool=helgrind ./t_p >o_hp 2>&1; valgrind --tool=helgrind ./v_n >o_hn 2>&1
row "valgrind helgrind" $(chk o_hp "Possible data race") $(grep -q "ERROR SUMMARY: 0 errors" o_hn && echo SILENT || echo FIRED)
