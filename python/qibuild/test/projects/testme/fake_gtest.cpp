#include <iostream>
#include <fstream>

int main(int argc, char* argv[])
{
  if (argc < 1)
  {
    std::cerr << "Wrong number of arguments" << std::endl
              << "Usage fake_gtest OUTPUT_XML" << std::endl;
    return 2;
  }
  char* output = argv[1];
  std::ofstream ofs;
  ofs.open(output);
  ofs << "<gtest>FAKE_RESULTS</gtest>" << std::endl;

  return 1;
}
