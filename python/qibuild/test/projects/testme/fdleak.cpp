#include <fcntl.h>

int main() {
  int f = open("/dev/zero", O_RDONLY);
  return 0;
}
