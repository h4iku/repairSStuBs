import jpype
import jpype.imports
from jpype.types import *

normalizer_jar_path = "line-normalizer/target/line-normalizer-1.0-SNAPSHOT.jar"
jpype.startJVM(classpath=[normalizer_jar_path])

import java.lang
from java.lang import System
print(System.getProperty("java.class.path"))

from com.github.h4iku import Test


def check_line(src_file, line_number):
    pass
