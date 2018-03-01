from conans import ConanFile, AutoToolsBuildEnvironment, tools, CMake
import os


class ApacheaprConan(ConanFile):
    name = "apache-apr"
    version = "1.5.2"
    license = "Apache-2.0"
    url = "https://github.com/mkovalchik/conan-apache-apr"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    lib_name = "apr-" + version

    def source(self):
        file_ext = ".tar.gz" if not self.settings.os == "Windows" else "-win32-src.zip"
        tools.get("http://archive.apache.org/dist/apr/apr-{v}{ext}".format(v=self.version, ext=file_ext))

    def build(self):
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
            cmake = CMake(self)
            cmake.configure(source_folder=self.lib_name)
            cmake.build()
            cmake.install()
        else:
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(configure_dir=self.lib_name,  #os.path.join(self.source_folder, self.lib_name),
                                args=['--prefix', self.package_folder, ],
                                build=False)  # TODO: Workaround: in docker with x64 kernel AutoTools passes --build=x86_64 to 'cofigure' converting it into a cross-compilation
            env_build.make()
            env_build.make(args=['install'])

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
