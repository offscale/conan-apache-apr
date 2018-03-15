#include <iostream>
#include <apr_general.h>
#include <apr_version.h>

int main(int argc, char* argv[]) {
    const char* const* test = argv;
    apr_app_initialize(&argc, &test, 0);
    apr_terminate();
    std::cout << "apache-apr version: " << apr_version_string() << std::endl;
    return 0;
}
