
import os
import glob

from conans import ConanFile, AutoToolsBuildEnvironment, tools, CMake


class ApacheAPR(ConanFile):
    name = "apache-apr"
    version = "1.6.3"
    url = "https://github.com/jgsogo/conan-apache-apr"
    homepage = "https://apr.apache.org/"
    license = "http://www.apache.org/LICENSE.txt"
    description = "The mission of the Apache Portable Runtime (APR) project is to create and maintain " \
                  "software libraries that provide a predictable and consistent interface to underlying " \
                  "platform-specific implementations."
    exports_sources = ["LICENSE", "patches/*.patch" ]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"

    lib_name = "apr-" + version

    def configure(self):
        del self.settings.compiler.libcxx  # It is a C library

    def source(self):
        file_ext = ".tar.gz" if not self.settings.os == "Windows" else "-win32-src.zip"
        tools.get("http://archive.apache.org/dist/apr/apr-{v}{ext}".format(v=self.version, ext=file_ext))

    def patch(self):
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            tools.replace_in_file(os.path.join(self.lib_name, 'CMakeLists.txt'),
                                  "SET(install_bin_pdb ${install_bin_pdb} ${PROJECT_BINARY_DIR}/libapr-1.pdb)",
                                  "SET(install_bin_pdb ${install_bin_pdb} ${PROJECT_BINARY_DIR}/bin/libapr-1.pdb)")

        if self.settings.os == "Windows" and self.settings.compiler == "gcc":  # MinGW builds
            # Apply patch inspired in this one: https://bz.apache.org/bugzilla/show_bug.cgi?id=51724
            tools.patch(base_path=self.lib_name, patch_file=os.path.join("patches", "mingw.patch"))


    def build(self):
        self.patch()

        if self.settings.os == "Windows" and self.settings.compiler == "gcc":  # MinGW build
            with tools.chdir(self.lib_name):
                # Problem compiling with 64 bits due to flags: https://wiki.apache.org/logging-log4cxx/MSWindowsBuildInstructions
                # Build instructions taken from apache-log4cxx: https://sourceforge.net/p/mingw-w64/discussion/723798/thread/baa59718/
                self.run("./buildconf", win_bash=True)
                self.run("./configure CFLAGS=\"-O0 -s -mms-bitfields\" CXXFLAGS=\"-O0 -s -mms-bitfields\"", win_bash=True)
                self.run("make && make install")
        elif self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure(source_folder=self.lib_name)
            cmake.build()
            cmake.install()
        else:
            env_build = AutoToolsBuildEnvironment(self)
            env_build.fpic = True
            env_build.configure(configure_dir=self.lib_name, args=['--prefix', self.package_folder, ], build=False)
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        self.copy("LICENSE", src=self.lib_name)

        # And I modify deployed folder a little bit given config options (needed in Mac to link against desired libs)
        if self.options.shared:
            for f in glob.glob(os.path.join(self.package_folder, "lib", "*.a")):
                os.remove(f)
        else:
            for f in glob.glob(os.path.join(self.package_folder, "lib", "*.dylib")):
                os.remove(f)
            for f in glob.glob(os.path.join(self.package_folder, "lib", "*.so*")):
                os.remove(f)
            for f in glob.glob(os.path.join(self.package_folder, "lib", "*.la")):
                os.remove(f)

    def package_info(self):
        if self.settings.os == "Windows":
            if self.options.shared:
                libs = ["libapr-1", "libaprapp-1", ]
            else:
                libs = ["apr-1", "aprapp-1", "ws2_32", "Rpcrt4", ]
                self.cpp_info.defines = ["APR_DECLARE_STATIC", ]
        else:
            libs = ["apr-1", ]
            if not self.options.shared:
                libs += ["pthread", ]
            self.cpp_info.includedirs = [os.path.join("include", "apr-1"), ]
        self.cpp_info.libs = libs
