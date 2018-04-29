# nagios-plugin-oracle-java-updates

Nagios plugin to check updates for Oracle Java.

## Authors

Mohamed El Morabity <melmorabity -(at)- fedoraproject.org>

## Usage

    check_oracle_java_updates.py [--security-only] [--java-home]

### Options

    -h, --help

Show help message and exit.

    -s, --security-only

Only check security baselines.

    -j, --java-home

Path to the Oracle Java installation directory.

## Examples

    $ ./check_oracle_java_updates.py --java-home /opt/jdk1.8.0_141/
    Warning - Oracle Java 1.8.0_144 available

    $ ./check_oracle_java_updates.py --java-home /opt/jdk1.8.0_141/ --security-only
    OK - Oracle Java 1.8.0_141 is up-to-date

    $ ./check_oracle_java_updates.py --java-home /opt/jdk1.6.0_45
    Critical - No more public updates available for Oracle Java 1.6.0

    $ which java
    /usr/bin/java
    $ java -version
    openjdk version "1.8.0_144"
    OpenJDK Runtime Environment (build 1.8.0_144-b01)
    OpenJDK 64-Bit Server VM (build 25.144-b01, mixed mode)
    $ ./check_oracle_java_updates.py
    Unknown - No Oracle Java found

## Notes

This Nagios plugin relies on the [web service](https://java.com/applet/javaLatestVersion.xml) used by the Java browser applet on https://www.java.com/en/download/installed.jsp to check installed Java version.
