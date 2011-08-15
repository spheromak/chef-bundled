%define bundlename chef-server
%define rubyabi 1.9
%define rubyver 1.9.0
%define bundler_install_to  /usr/local
%define arch x86_64
%define chef_ver 0.10.4
%define chef_user chef
%define chef_group chef

# move src files to its own dir
%define _sourcedir     %{_topdir}/src/chef-server

Name: %{bundlename}
Version: %{chef_ver}
Release: 1%{?dist}
Summary: Monolithic chef-server  includes api/slice/solr in one go (via bundler)
Group: Development/Languages
License: ASL 2.0
URL: http://wiki.opscode.com/display/chef


Requires: ruby >= %{rubyver}
Requires: ruby(rubygems)
Requires: ruby(abi) = %{rubyabi}
Requires: rubygem(bundler)

Requires: chef
Requires: couchdb
Requires: rabbitmq-server
Requires: gecode

Requires(pre): shadow-utils
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(postun): initscripts

BuildRequires: gecode-devel

Provides: %{bundlename} = %{version}
Provides: chef-server-api = %{version}
Provides: chef-server-webui = %{version}
Provides: chef-solr = %{version}

Source1: server.rb
Source2: solr.rb
Source3: webui.rb

#BuildArch: %{arch}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u} -n)


%description 
The Chef Server is a Merb application that provides centralized storage and
distribution for recipes stored in "cookbooks," management and authentication
of client nodes and node data, and search indexes for that data.

This build inclides server  api  webui and solr support in one package under bundler

%prep
%setup  -c -T

echo "source \"http://rubygems.org\" " > Gemfile
echo 'gem "mixlib-log", "1.3.0" ' >> Gemfile
echo "gem \"chef\", \"%{version}\" "  >>  Gemfile
echo "gem \"chef-expander\", \"%{version}\" "  >>  Gemfile
echo "gem \"chef-server-api\", \"%{version}\" "  >> Gemfile
echo "gem \"chef-solr\", \"%{version}\" "  >> Gemfile
echo "gem \"chef-server-webui\", \"%{version}\" "  >> Gemfile
echo "gem \"rack\" "  >> Gemfile

%build
bundle install --binstubs     --path %{name}-bundle
bundle package
bundle install --path %{name}-bundle --deployment   --binstubs --local




%install
rm -rf %{buildroot}
mkdir -p %{buildroot}

# copy BUILD to BUILDROOT
mkdir -p %{buildroot}/%{bundler_install_to}/%{name}
mv *  %{buildroot}/%{bundler_install_to}/%{name}
mv .bundle %{buildroot}/%{bundler_install_to}/%{name}/

mkdir -p %{buildroot}%{_bindir}

cd  %{buildroot}

bins=( chef-server chef-solr chef-expander  chef-solr-installer chef-expanderctl chef-server-webui chef-solr-rebuild )
for i in ${bins[@]} ; do
  ln -s %{bundler_install_to}/%{name}/bin/$i $(echo -n %{_bindir} | sed 's/^\///')/$i
done

mkdir -p %{buildroot}%{_localstatedir}/{log/chef,run/chef,cache/chef}

# quick def to make this shorter
chef_rhel=%{buildroot}%{bundler_install_to}/%{name}/%{name}-bundle/ruby/1.9.1/gems/chef-%{version}/distro/redhat/etc

for i in chef-server chef-expander chef-solr chef-server-webui ; do 
  install -Dp -m0644 $chef_rhel/logrotate.d/$i %{buildroot}%{_sysconfdir}/logrotate.d/$i
  install -Dp -m0755 $chef_rhel/init.d/$i      %{buildroot}%{_initrddir}/$i
  install -Dp -m0644 $chef_rhel/sysconfig/$i   %{buildroot}%{_sysconfdir}/sysconfig/$i
done

install -Dp -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/chef/server.rb
install -Dp -m0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/chef/solr.rb
install -Dp -m0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/chef/webui.rb

cd %{buildroot}/etc/chef
ln -s solr.rb  expander.rb 


# Oh, those wacky developers.
find %{buildroot}%{bundler_install_to} -type f | \
  xargs -n 1 sed -i -e 's"^#!/usr/bin/env ruby"#!/usr/bin/ruby"'

find %{buildroot}%{bundler_install_to} -type f | \
  xargs -n 1 sed -i -e 's"^#!/usr/local/ruby"#!/usr/bin/ruby"'

find %{buildroot}%{bundler_install_to} -type f | \
  xargs -n 1 sed -i -e 's"^#!/usr/local/bin/ruby"#!/usr/bin/ruby"'

find %{buildroot}%{bundler_install_to} -type f | \
  xargs -n 1 sed -i -e 's"/System/Library/Frameworks/Ruby.framework/Versions/1.8/usr/bin/ruby"#!/usr/bin/ruby"' 


%clean
rm -rf %{buildroot}

%post 
/sbin/chkconfig --add chef-server
/sbin/chkconfig --add chef-server-webui
/sbin/chkconfig --add chef-solr
/sbin/chkconfig --add chef-expander



%preun 
if [ $1 -eq 0 ]; then
  /sbin/service chef-server stop > /dev/null 2>&1 || :
  /sbin/service chef-solr stop > /dev/null 2>&1 || :
  /sbin/service chef-expander stop > /dev/null 2>&1 || :
  /sbin/chkconfig --del chef-server
  /sbin/chkconfig --del chef-solr
  /sbin/chkconfig --del chef-expander
  /sbin/chkconfig --del chef-server-webui 
fi


%postun 
if [ "$1" -ge "1" ] ; then
    /sbin/service chef-server condrestart >/dev/null 2>&1 || :
    /sbin/service chef-solr condrestart >/dev/null 2>&1 || :
    /sbin/service chef-expander condrestart >/dev/null 2>&1 || :
fi


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

%attr(-,%{chef_user},root) %dir %{_localstatedir}/log
%attr(-,%{chef_user},root) %dir %{_localstatedir}/cache
%attr(-,%{chef_user},root) %dir %{_localstatedir}/run

%config(noreplace) /etc/chef/server.rb
%config(noreplace) /etc/chef/solr.rb
%config(noreplace) /etc/sysconfig/chef-expander
%config(noreplace) /etc/sysconfig/chef-server
%config(noreplace) /etc/sysconfig/chef-solr


