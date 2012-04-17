#include <iostream>
#include <fstream>

int main(int argc, char* argv[])
{
  if(argc < 3) {
    std::cerr << "Usage footool IN OUT" << std::endl;
    return 2;
  }

  char* in = argv[1];
  char* out = argv[2];
  std::fstream infile;
  std::fstream outfile;

  infile.open(in, std::ios_base::in);

  if (! infile.is_open()) {
    std::cerr << "Could not open: '" << in << "' for reading" << std::endl;
    return 2;
  }

  outfile.open(out, std::ios_base::out | std::ios_base::trunc);
  if (! outfile.is_open()) {
    std::cerr << "Could not open: '" << out << "' for writing" << std::endl;
    return 2;
  }

  std::cout << "Running footol: " << in << " -> " << out << std::endl;
  outfile << infile.rdbuf();
  infile.close();
  outfile.close();
  return 0;
}
