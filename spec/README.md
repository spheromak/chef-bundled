
Building Multiarch
------------------
Easy way to get i386/x86_64 on the same system:
Install all the dependant libs for the target architecture then use setarch and --target to build for that arch

example:
    setarch i386 rpmbuild --target i386 -ba chef-server.spec

Pulling Gemfiles 
----------------
Use this command to grab a gem file from a gem
   gem fetch --remote  bundler

if you built an older rubygem you may need to specify --remote

Build Order
-----------
Generally want to build in this order
* libyaml
* ruby
* rubygems-bundler
* zeromq
* chef

NOTE:
-----
you probably want to setup your ~/.gemrc file like so:
    gem: --no-rdoc --no-ri 

this way you can keep your bundled chef size down a bit
