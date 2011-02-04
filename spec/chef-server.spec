%define bundlename chef-server
%define rubyabi 1.9
%define rubyver 1.9.0
%define bundler_install_to  /usr/local
%define arch x86_64
%define chef_ver 0.9.12
%define chef_user chef
%define chef_group chef

Name: %{bundlename}
Version: %{chef_ver}
Release: 2%{?dist}
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

Requires(pre): shadow-utils
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(postun): initscripts

Provides: %{bundlename} = %{version}
Provides: chef-server-api = %{version}
Provides: chef-server-webui = %{version}
Provides: chef-solr = %{version}

Source1: chef-server.logrotate
Source2: chef-server.init
Source3: chef-server.sysconf
Source4: server.rb

Source14: chef-solr.logrotate
Source15: chef-solr-indexer.logrotate
Source16: chef-solr.init
Source17: chef-solr-indexer.init
Source18: chef-solr.sysconf
Source19: chef-solr-indexer.sysconf
Source110: solr.rb
Source111: solr-indexer.rb

Source22: chef-server-webui.logrotate
Source23: chef-server-webui.init
Source24: chef-server-webui.sysconf
Source25: webui.rb



BuildArch: %{arch}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u} -n)


%description 
The Chef Server is a Merb application that provides centralized storage and
distribution for recipes stored in "cookbooks," management and authentication
of client nodes and node data, and search indexes for that data.

This build inclides server  api  webui and solr support in one package under bundler

%prep
%setup  -c -T

echo "source \"http://rubygems.org\" " > Gemfile
echo "gem \"chef\", \"%{version}\" "  >> Gemfile
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

bins=( chef-server chef-solr chef-solr-indexer chef-server-webui chef-solr-rebuild )
for i in ${bins[@]} ; do
  ln -s %{bundler_install_to}/%{name}/bin/$i $(echo -n %{_bindir} | sed 's/^\///')/$i
done

mkdir -p %{buildroot}%{_localstatedir}/{log/chef,run/chef,cache/chef}



install -Dp -m0644 \
  %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/chef-server

install -Dp -m0755 \
  %{SOURCE2} %{buildroot}%{_initrddir}/chef-server

install -Dp -m0644 \
  %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/chef-server

install -Dp -m0644 \
  %{SOURCE4} %{buildroot}%{_sysconfdir}/chef/server.rb


install -Dp -m0644 \
  %{SOURCE14} %{buildroot}%{_sysconfdir}/logrotate.d/chef-solr

install -Dp -m0644 \
  %{SOURCE15} %{buildroot}%{_sysconfdir}/logrotate.d/chef-solr-indexer

install -Dp -m0755 \
  %{SOURCE16} %{buildroot}%{_initrddir}/chef-solr

install -Dp -m0755 \
  %{SOURCE17} %{buildroot}%{_initrddir}/chef-solr-indexer

install -Dp -m0644 \
  %{SOURCE18} %{buildroot}%{_sysconfdir}/sysconfig/chef-solr

install -Dp -m0644 \
  %{SOURCE19} %{buildroot}%{_sysconfdir}/sysconfig/chef-solr-indexer

install -Dp -m0644 \
  %{SOURCE110} %{buildroot}%{_sysconfdir}/chef/solr.rb

install -Dp -m0644 \
  %{SOURCE111} %{buildroot}%{_sysconfdir}/chef/solr-indexer.rb


install -Dp -m0644 \
  %{SOURCE22} %{buildroot}%{_sysconfdir}/logrotate.d/chef-server-webui

install -Dp -m0755 \
  %{SOURCE23} %{buildroot}%{_initrddir}/chef-server-webui

install -Dp -m0644 \
  %{SOURCE24} %{buildroot}%{_sysconfdir}/sysconfig/chef-server-webui

install -Dp -m0644 \
  %{SOURCE25} %{buildroot}%{_sysconfdir}/chef/webui.rb



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
/sbin/chkconfig --add chef-solr-indexer



%preun 
if [ $1 -eq 0 ]; then
  /sbin/service chef-server stop > /dev/null 2>&1 || :
  /sbin/service chef-solr stop > /dev/null 2>&1 || :
  /sbin/service chef-solr-indexer stop > /dev/null 2>&1 || :
  /sbin/chkconfig --del chef-server
  /sbin/chkconfig --del chef-solr
  /sbin/chkconfig --del chef-solr-indexer
  /sbin/chkconfig --del chef-server-webui 
fi


%postun 
if [ "$1" -ge "1" ] ; then
    /sbin/service chef-server condrestart >/dev/null 2>&1 || :
    /sbin/service chef-solr condrestart >/dev/null 2>&1 || :
    /sbin/service chef-solr-indexer condrestart >/dev/null 2>&1 || :
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

