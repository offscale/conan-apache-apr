#include <iostream>
#include <apr-1/apr_general.h>
#include <apr-1/apr_version.h>

int main(int argc, char* argv[]) {
    const char* const* test = argv;
    apr_app_initialize(&argc, &test, 0);
    apr_terminate();
    std::cout << "apache-apr version: " << apr_version_string() << std::endl;
    return 0;
}
