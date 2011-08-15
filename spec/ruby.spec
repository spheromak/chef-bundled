#%define _prefix		/usr
#%define _localstatedir	/var
#%define _mandir		/usr/local/man
#%define _infodir	/usr/local/share/info

%define rubyver		1.9.2
%define rubyxver    1.9
%define rubyminorver  180
%define gems_version 1.3.7

%define sitedir     %{_libdir}/ruby/site_ruby


Name:		ruby
Version:	%{rubyver}.%{rubyminorver}
Release:	8%{?dist}
License:	Ruby License/GPL - see COPYING
URL:		http://www.ruby-lang.org/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	readline readline-devel ncurses ncurses-devel gdbm gdbm-devel glibc-devel  gcc unzip openssl-devel db4-devel byacc
Source0:	ftp://ftp.ruby-lang.org/pub/ruby/ruby-%{rubyver}-p%{rubyminorver}.tar.gz
Summary:	An interpreter of object-oriented scripting language
Group:		Development/Languages

Provides:ruby(abi) = 1.8
Provides:libruby.so.1.8
Provides:libruby.so.1.8()(64bit) 
Provides:ruby(abi) = %{rubyxver}
Provides:libruby = %{version}-%{release}
Provides:irb = %{version}-%{release}
Provides:rdoc = %{version}-%{release}
Provides:ri = %{version}-%{release}
Provides:ruby(rubygems) = %{gems_version}
Provides:rubygems
Provides:ruby-libs
Provides:ruby-rdoc
Provides:ruby-ri

Obsoletes:rubygems, ruby-rdoc, ruby-irb, ruby-libs, ruby-devel, ruby-ri

%description
Ruby is the interpreted scripting language for quick and easy
object-oriented programming.  It has many features to process text
files and to do system management tasks (as in Perl).  It is simple,
straight-forward, and extensible.

%prep
%setup -n ruby-%{rubyver}-p%{rubyminorver}
%build
CFLAGS="$RPM_OPT_FLAGS -Wall -fno-strict-aliasing"
export CFLAGS
%configure --with-sitedir='%{sitedir}' --enable-shared  --with-ruby-prefix=%{_prefix}/lib --disable-rpath

make RUBY_INSTALL_NAME=ruby %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

# installing binaries ...
make install DESTDIR=$RPM_BUILD_ROOT
cd  $RPM_BUILD_ROOT/%{_libdir}
ln -s libruby.so.1.9  libruby.so.1.8


%clean
rm -rf $RPM_BUILD_ROOT

%files 
%defattr(-, root, root)
%doc README COPYING ChangeLog LEGAL ToDo 
%{_prefix}/*

%changelog
* Fri Nov 15 2010 Taylor Kimball <taylor@linuxhq.org> - 1.9.2-p0-1
- Initial build for el5 based off of el5 spec.
