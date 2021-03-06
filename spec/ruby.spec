#%define _prefix		/usr
#%define _localstatedir	/var
#%define _mandir		/usr/local/man
#%define _infodir	/usr/local/share/info

%define rubyver		1.9.3
%define rubyxver    1.9
%define rubyminorver  194
%define gems_version 1.8.24
%define rev 3
%define sitedir     %{_libdir}/ruby/site_ruby


Name:		ruby
Version:	%{rubyver}.%{rubyminorver}
Release:	%{rev}%{?dist}
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
Provides:ri = %{version}-%{release}
Provides:ruby(rubygems) = %{gems_version}
Provides:rubygems
Provides:ruby-libs
Provides:ruby-rdoc
Provides:rdoc = %{version}-%{release}

Obsoletes:rubygems, ruby-rdoc, ruby-irb, ruby-libs, ruby-devel, ruby-ri

%description
Ruby is the interpreted scripting language for quick and easy
object-oriented programming.  It has many features to process text
files and to do system management tasks (as in Perl).  It is simple,
straight-forward, and extensible.

%package doc
Summary: Ruby documentation
Group:  Development/Libraries  
Provides:ruby-ri
%description doc
Ruby Documentation broken into its own package. Includes ruby-ri 

%prep
%setup -n ruby-%{rubyver}-p%{rubyminorver}
%build
CFLAGS="$RPM_OPT_FLAGS -Wall -fno-strict-aliasing"
export CFLAGS

%configure --enable-shared \
  --disable-rpath \
  --without-X11 \
  --without-tk \
  --includedir=%{_includedir}/ruby \
  --libdir=%{_libdir} \
  --with-sitedir='%{sitedir}' \
  --with-ruby-prefix=%{_prefix}/lib 

make RUBY_INSTALL_NAME=ruby %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

# installing binaries ...
make install DESTDIR=$RPM_BUILD_ROOT
cd  $RPM_BUILD_ROOT/%{_libdir}
ln -s libruby.so.1.9  libruby.so.1.8
rm -rf  $RPM_BUILD_ROOT/usr/src

%clean
rm -rf $RPM_BUILD_ROOT

%files doc
%defattr(-, root, root)
%doc README COPYING ChangeLog LEGAL ToDo 
%doc %{_prefix}/share/ri
%doc %{_prefix}/share/doc

%files 
%defattr(-, root, root)
%{_prefix}/bin
%{_prefix}/include  
%{_prefix}/lib64  
%{_prefix}/local

%changelog
* Fri May 25 2012 Jesse Nelson <spheormak@gmail.com> - 1.9.3-p194-3
- update for 194 
- break doc and ri out to their own package

* Fri Nov 15 2010 Taylor Kimball <taylor@linuxhq.org> - 1.9.2-p0-1
- Initial build for el5 based off of el5 spec.
