%define bundlename chef
%define rubyabi 1.9
%define rubyver 1.9.0
%define bundler_install_to  /usr/local
%define chef_ver 0.10.10
%define rel_ver  3
%define chef_user chef
%define chef_group chef

# move src files to its own dir
%define _sourcedir     %{_topdir}/src/chef

Name: %{bundlename}
Version: %{chef_ver}
Release: %{rel_ver}%{?dist}
Summary: Client and libraries for Chef systems integration framework
Group: Development/Languages
License: ASL 2.0
URL: http://wiki.opscode.com/display/chef

Source5: chef-client.logrotate
Source6: chef-client.init
Source7: client.rb
Source8: solo.rb
Source9: chef-client.sysconf
Source999: Gemfile

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u} -n)

BuildRequires: rpm-devel
BuildRequires: ruby >= %{rubyver}

Requires: ruby >= %{rubyver}
Requires: ruby(rubygems)
Requires: ruby(abi) = %{rubyabi}
Requires: rubygem(bundler)
Provides: %{bundlename} = %{version}
Provides: chef-client = %{version}
Obsoletes: chef-common, chef-client, rubygem-chef, ohai, rubygem-ohai

Requires(pre): shadow-utils
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(postun): initscripts


%description 
Chef is a systems integration framework and configuration management library
written in Ruby. Chef provides a Ruby library and API that can be used to
bring the benefits of configuration management to an entire infrastructure.

Chef can be run as a client (chef-client) to a server, or run as a standalone
tool (chef-solo). Configuration recipes are written in a pure Ruby DSL.

This build of chef uses non-pristine source, as outputted by gembundler to package
chef's dependencies into /opt so that the user does not have to worry about
system rubygem version compatability.


%prep
%setup  -c  -T
rm -rf ${buildroot}

if [ -f %{SOURCE999} ] ; then
   echo "using  Gemfile %{SOURCE999}"
   echo "if you define %{name} in your Gemfile well error out "
   cp %{SOURCE999} Gemfile
else
   echo "no Gemfile found making a basic one"
   bundle init
fi

echo 'gem "mixlib-log"  ' >> Gemfile
echo 'gem "net-ssh-multi" ' >> Gemfile
echo 'gem "knife-flow" ' >> Gemfile
echo 'gem "knife-github-cookbooks" ' >> Gemfile
echo 'gem "minitest" ' >> Gemfile
echo 'gem "minitest-chef-handler" ' >> Gemfile
echo 'gem "ruby-shadow"' >> Gemfile
echo 'gem "xml-simple"' >> Gemfile
echo "gem \"%{name}\", \"%{version}\" "  >> Gemfile



%build
bundle install --path %{name}-bundle  --binstubs 
bundle package 



%install
rm -rf %{buildroot}
mkdir -p %{buildroot}

# copy BUILD to BUILDROOT
mkdir -p %{buildroot}/%{bundler_install_to}/%{name}
mv *  %{buildroot}/%{bundler_install_to}/%{name}
mv .bundle %{buildroot}/%{bundler_install_to}/%{name}/

mkdir -p %{buildroot}%{_bindir}

cd  %{buildroot}

bins=( shef  chef-client knife chef-solo ohai)
for i in ${bins[@]} ; do
  ln -s %{bundler_install_to}/%{name}/bin/$i $(echo -n %{_bindir} | sed 's/^\///')/$i
done



mkdir -p %{buildroot}%{_localstatedir}/{log/chef,run/chef,cache/chef}


install -Dp -m0644 \
  %{SOURCE5} %{buildroot}%{_sysconfdir}/logrotate.d/chef-client

install -Dp -m0755 \
  %{SOURCE6} %{buildroot}%{_initrddir}/chef-client

install -Dp -m0644 \
  %{SOURCE9} %{buildroot}%{_sysconfdir}/sysconfig/chef-client

# write chef config files
install -Dp -m0644 \
  %{SOURCE7} %{buildroot}%{_sysconfdir}/chef/client.rb
install -Dp -m0644 \
  %{SOURCE8} %{buildroot}%{_sysconfdir}/chef/solo.rb



# fix up busted  gem paths
find %{buildroot}%{bundler_install_to} -type f | \
  xargs -n 1 sed -i -e 's"^#!/usr/local/bin/ruby"#!/usr/bin/ruby"'

%clean
rm -rf %{buildroot}



%pre
getent group %{chef_group} >/dev/null || groupadd -r %{chef_group}
getent passwd %{chef_user} >/dev/null || \
useradd -r -g %{chef_group} -d %{_localstatedir}/lib/chef -s /sbin/nologin \
  -c "Chef user" %{chef_user}
exit 0



%files
%defattr(-,root,root,-)
%{bundler_install_to}/%{name}
%{_bindir}
%{_sysconfdir}
%{_initrddir}

%attr(-,%{chef_user},root) %dir %{_localstatedir}/log/chef
%attr(-,%{chef_user},root) %dir %{_localstatedir}/cache/chef
%attr(-,%{chef_user},root) %dir %{_localstatedir}/run/chef


%config(noreplace) /etc/chef/client.rb
%config(noreplace) /etc/sysconfig/chef-client





