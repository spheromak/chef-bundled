%define bundlename chef-server
%define rubyabi 1.9
%define rubyver 1.9.0
%define bundler_install_to  /usr/local
%define arch x86_64
%define chef_ver 0.10.10
%define rel 3
%define chef_user chef
%define chef_group chef
%define components  "chef-server" "chef-expander" "chef-server-webui" "chef-solr"
# move src files to its own dir
%define _sourcedir     %{_topdir}/src/chef-server

Name: %{bundlename}
Version: %{chef_ver}
Release: %{rel}%{?dist}
Summary: Monolithic chef-server  includes api/slice/solr in one go (via bundler)
Group:  System Environment/Daemons
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
Source4: chef-create-amqp_passwd

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u} -n)


%description 
The Chef Server is a Merb application that provides centralized storage and
distribution for recipes stored in "cookbooks," management and authentication
of client nodes and node data, and search indexes for that data.

This build inclides server api and solr support in one package under bundler

%package -n chef-solr
Summary: chef-solr is the solr server for chef servers 
Group:  System Environment/Daemons
%description -n chef-solr
Thin wrapper around  java solr includes jetty and solr application

%package -n chef-expander
Summary: Chef-expander 
Group:  System Environment/Daemons
%description -n chef-expander
The chef expander is the rabbitmq consumer for generating index data to send to solr instances expanders can reside on many nodes not just the server itself.

%package webui
Summary: chef-server-webui package 
Group:  System Environment/Daemons
%description webui
The chef-server-webui is the administrative web interface to the chef server api. This package is independant of the server pacakge, but will require confugration to use against a sepparate chef-server


%prep
%setup  -c -T
for i in %{components} ; do 
  mkdir $i
done 

# chef-chef-server server/Gemfile
echo "source \"http://rubygems.org\" " > chef-server/Gemfile
echo 'gem "mixlib-log"' >> chef-server/Gemfile
echo "gem \"chef\", \"%{version}\" "  >> chef-server/Gemfile
echo "gem \"chef-server-api\", \"%{version}\" "  >> chef-server/Gemfile
echo "gem \"yajl-ruby\" " >> chef-server/Gemfile
echo "gem \"json\" " >> chef-server/Gemfile
echo "gem \"coderay\" " >> chef-server/Gemfile

# chef-solr gemfile
echo "source \"http://rubygems.org\" " > chef-solr/Gemfile
echo "gem \"chef-solr\", \"%{version}\" "  >> chef-solr/Gemfile

# chef-expander gemfile
echo "source \"http://rubygems.org\" " > chef-expander/Gemfile
echo "gem \"chef-expander\", \"%{version}\" "  >>  chef-expander/Gemfile

# webui gemfile
echo "source \"http://rubygems.org\" " > chef-server-webui/Gemfile
echo "gem \"chef-server-webui\", \"%{version}\" "  >> chef-server-webui/Gemfile
echo "gem \"rack\" "  >> chef-server-webui/Gemfile


%build
for i in %{components} ; do
  cd $i
  bundle install --binstubs  --path $i-bundle
  bundle package
  bundle install --path $i-bundle --deployment   --binstubs --local
  cd ..
done



%install
rm -rf %{buildroot}
mkdir -p %{buildroot}

# copy BUILD to BUILDROOT
for i in %{components} ; do
  mkdir -p %{buildroot}/%{bundler_install_to}/
  mv $i  %{buildroot}/%{bundler_install_to}/
done

mkdir -p %{buildroot}%{_bindir}

cd  %{buildroot}
server_bins=(chef-server)
webui_bins=(chef-server-webui)
solr_bins=(chef-solr-installer chef-solr chef-solr-rebuild) 
expander_bins=(chef-expander chef-expanderctl)

for i in ${expander_bins[@]} ; do
  ln -s %{bundler_install_to}/chef-expander/bin/$i $(echo -n %{_bindir} | sed 's/^\///')/$i
done

for i in ${solr_bins[@]} ; do
  ln -s %{bundler_install_to}/chef-solr/bin/$i $(echo -n %{_bindir} | sed 's/^\///')/$i
done

for i in ${webui_bins[@]} ; do
  ln -s %{bundler_install_to}/chef-server-webui/bin/$i $(echo -n %{_bindir} | sed 's/^\///')/$i
done

for i in ${server_bins[@]} ; do
  ln -s %{bundler_install_to}/chef-server/bin/$i $(echo -n %{_bindir} | sed 's/^\///')/$i
done

# create all the state dirs
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
# aqmp passwd stuffs
install -Dp -m0755 \
  %{SOURCE4} %{buildroot}%{_sbindir}/chef-create-amqp_passwd

cd %{buildroot}/etc/chef
ln -s solr.rb  expander.rb 




%clean
rm -rf %{buildroot}

%post 
/sbin/chkconfig --add chef-server

%post webui
/sbin/chkconfig --add chef-server-webui

%post -n chef-solr
/sbin/chkconfig --add chef-solr

%post -n chef-expander
/sbin/chkconfig --add chef-expander



%preun 
if [ $1 -eq 0 ]; then
  /sbin/service chef-server stop > /dev/null 2>&1 || :
  /sbin/chkconfig --del chef-server
fi

%preun  -n chef-solr
if [ $1 -eq 0 ]; then
  /sbin/service chef-solr stop > /dev/null 2>&1 || :
  /sbin/chkconfig --del chef-solr
fi 

%preun -n chef-expander
if [ $1 -eq 0 ]; then
  /sbin/service chef-expander stop > /dev/null 2>&1 || :
  /sbin/chkconfig --del chef-expander
fi

%preun webui
if [ $1 -eq 0] ; then 
  /sbin/service chef-server-webui stop > /dev/null 2>&1 || :
  /sbin/chkconfig --del chef-server-webui 
fi

%postun 
if [ "$1" -ge "1" ] ; then
    /sbin/service chef-server condrestart >/dev/null 2>&1 || :
fi

%postun  webui
if [ "$1" -ge "1" ] ; then
    /sbin/service chef-server-webui condrestart >/dev/null 2>&1 || :
fi

%postun -n chef-solr
if [ "$1" -ge "1" ] ; then
    /sbin/service chef-solr condrestart >/dev/null 2>&1 || :
fi

%postun -n chef-expander
if [ "$1" -ge "1" ] ; then
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
%{bundler_install_to}/chef-server
%{_bindir}/chef-server
%{_initrddir}/chef-server
%attr(0755,root,root)  /usr/sbin/chef-create-amqp_passwd
%attr(-,%{chef_user},root) %dir %{_localstatedir}/log
%attr(-,%{chef_user},root) %dir %{_localstatedir}/cache
%attr(-,%{chef_user},root) %dir %{_localstatedir}/run
%config(noreplace) %{_sysconfdir}/sysconfig/chef-server
%config(noreplace) %{_sysconfdir}/chef/server.rb
%config(noreplace) %{_sysconfdir}/logrotate.d/chef-server

%files webui
%{bundler_install_to}/chef-server-webui
%{_bindir}/chef-server-webui
%{_initrddir}/chef-server-webui
%attr(-,%{chef_user},root) %dir %{_localstatedir}/log
%attr(-,%{chef_user},root) %dir %{_localstatedir}/cache
%attr(-,%{chef_user},root) %dir %{_localstatedir}/run
%config(noreplace) %{_sysconfdir}/sysconfig/chef-server-webui
%config(noreplace) %{_sysconfdir}/chef/webui.rb
%config(noreplace) %{_sysconfdir}/logrotate.d/chef-server-webui

%files -n chef-solr
%{bundler_install_to}/chef-solr
%{_bindir}/chef-solr-installer
%{_bindir}/chef-solr
%{_bindir}/chef-solr-rebuild
%{_initrddir}/chef-solr
%attr(-,%{chef_user},root) %dir %{_localstatedir}/log
%attr(-,%{chef_user},root) %dir %{_localstatedir}/cache
%attr(-,%{chef_user},root) %dir %{_localstatedir}/run
%config(noreplace) %{_sysconfdir}/sysconfig/chef-solr
%config(noreplace) %{_sysconfdir}/chef/solr.rb
%config(noreplace) %{_sysconfdir}/logrotate.d/chef-solr

%files -n chef-expander
%{bundler_install_to}/chef-expander
%{_bindir}/chef-expander 
%{_bindir}/chef-expanderctl
%{_initrddir}/chef-expander
%attr(-,%{chef_user},root) %dir %{_localstatedir}/log
%attr(-,%{chef_user},root) %dir %{_localstatedir}/cache
%attr(-,%{chef_user},root) %dir %{_localstatedir}/run
%config(noreplace) %{_sysconfdir}/sysconfig/chef-expander
%config(noreplace) %{_sysconfdir}/chef/expander.rb
%config(noreplace) %{_sysconfdir}/chef/solr.rb
%config(noreplace) %{_sysconfdir}/logrotate.d/chef-expander

