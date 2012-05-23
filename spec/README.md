
Building Multiarch
------------------
Easy way to get i386/x86_64 on the same system:
Install all the dependant libs for the target architecture then use setarch and --target to build for that arch

example:

    setarch i386 rpmbuild --target i386 -ba chef-server.spec

Build Order
-----------
Generally want to build in this order
* libyaml
* ruby
* rubygems-bundler
* zeromq
* chef
