from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os

class ApacheaprConan(ConanFile):
    name = "apache-apr"
    version = "1.5.2"
    license = "Apache-2.0"
    url = "https://github.com/mkovalchik/conan-apache-apr"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    lib_name = name + "-" + version

    def source(self):
        file_ext = ".tar.gz" if not self.settings.os == "Windows" else "-win32-src.zip"
        tools.download("https://www.apache.org/dyn/mirrors/mirrors.cgi?action=download&filename=apr/apr-" + self.version + file_ext, self.lib_name + file_ext)
        tools.unzip(self.lib_name + file_ext)

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            configure_command = "./configure"
            if self.settings.os == "Windows":
                configure_command = configure_command + ".bat"

            include_dir = os.path.join(os.getcwd(), "include")
            lib_dir = os.path.join(os.getcwd(), "lib")
            configure_command = configure_command + " --prefix=" + os.getcwd()

            with tools.chdir("apr-" + self.version):
                self.run(configure_command)
                self.run("make -j " + str(max(tools.cpu_count() - 1, 1)))
                self.run("make install ")

    def package(self):
        self.copy("*.so*", dst="lib", src="lib", keep_path=False)
        self.copy("*.a", dst="lib", src="lib", keep_path=False)
        self.copy("*.h", dst="include", src="include", keep_path=True)
        self.copy("apr-config", dst="bin", src="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libs = ["apr-1"]
