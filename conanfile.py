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
    lib_name = name + "-" + version

    def source(self):
        file_ext = ".tar.gz" if not self.settings.os == "Windows" else "-win32-src.zip"
        tools.download("http://archive.apache.org/dist/apr/apr-" + self.version + file_ext, self.lib_name + file_ext)
        tools.unzip(self.lib_name + file_ext)

    def build(self):
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                tools.replace_in_file(os.path.join("apr-{v}".format(v=self.version), 'CMakeLists.txt'),
                                      "SET(install_bin_pdb ${install_bin_pdb} ${PROJECT_BINARY_DIR}/libapr-1.pdb)",
                                      "SET(install_bin_pdb ${install_bin_pdb} ${PROJECT_BINARY_DIR}/Debug/libapr-1.pdb)")
            cmake = CMake(self)
            cmake.configure(source_folder="apr-" + self.version)
            cmake.build()
            cmake.install()
        else:
            env_build = AutoToolsBuildEnvironment(self)
            with tools.environment_append(env_build.vars):
                self.run("./configure --prefix={}".format(self.package_folder))
                self.run("make")
                self.run("make install")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
