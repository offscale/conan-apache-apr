from conans import ConanFile, AutoToolsBuildEnvironment, tools, CMake
import os


class ApacheAPR(ConanFile):
    name = "apache-apr"
    version = "1.6.3"
    url = "https://github.com/jgsogo/conan-apache-apr"
    homepage = "https://apr.apache.org/"
    license = "http://www.apache.org/LICENSE.txt"
    exports_sources = ["LICENSE",]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    lib_name = "apr-" + version

    def source(self):
        file_ext = ".tar.gz" if not self.settings.os == "Windows" else "-win32-src.zip"
        tools.get("http://archive.apache.org/dist/apr/apr-{v}{ext}".format(v=self.version, ext=file_ext))

    def patch(self):
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                tools.replace_in_file(os.path.join(self.lib_name, 'CMakeLists.txt'),
                                      "SET(install_bin_pdb ${install_bin_pdb} ${PROJECT_BINARY_DIR}/libapr-1.pdb)",
                                      "SET(install_bin_pdb ${install_bin_pdb} ${PROJECT_BINARY_DIR}/Debug/libapr-1.pdb)")
            tools.replace_in_file(os.path.join(self.lib_name, 'CMakeLists.txt'),
                                  "INSTALL(FILES ${APR_PUBLIC_HEADERS_STATIC} ${APR_PUBLIC_HEADERS_GENERATED} DESTINATION include)",
                                  "INSTALL(FILES ${APR_PUBLIC_HEADERS_STATIC} ${APR_PUBLIC_HEADERS_GENERATED} DESTINATION include/apr-1)")
            tools.replace_in_file(os.path.join(self.lib_name, 'CMakeLists.txt'),
                                  "  INSTALL(FILES ${APR_PRIVATE_H_FOR_HTTPD} DESTINATION include/arch/win32)",
                                  "  INSTALL(FILES ${APR_PRIVATE_H_FOR_HTTPD} DESTINATION include/apr-1/arch/win32)")
            tools.replace_in_file(os.path.join(self.lib_name, 'CMakeLists.txt'),
                                  "INSTALL(FILES include/arch/apr_private_common.h DESTINATION include/arch)",
                                  "INSTALL(FILES include/arch/apr_private_common.h DESTINATION include/apr-1/arch)")

    def build(self):
        self.patch()
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure(source_folder=self.lib_name)
            cmake.build()
            cmake.install()
        else:
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(configure_dir=self.lib_name, args=['--prefix', self.package_folder, ])
            env_build.make()
            env_build.make(args=['install'])

    def package_id(self):
        self.info.options.shared = "Any"  # Both, shared and not are built always

    def package_info(self):
        if self.options.shared:
            libs = ["libapr-1", "libaprapp-1", ]
        else:
            self.cpp_info.defines = ["APR_DECLARE_STATIC", ]
            libs = ["apr-1", "aprapp-1", ]
            if self.settings.os == "Windows":
                libs += ["ws2_32", "Rpcrt4", ]
        self.cpp_info.libs = libs
