Name:           gecode
Version:        3.5.0
Release:        1%{?dist}
Summary:        Generic constraint development environment

Group:          System Environment/Libraries
License:        MIT
URL:            http://www.gecode.org/
Source0:        http://www.gecode.org/download/%{name}-%{version}.tar.gz
Patch0:         gecode-3.5.0-no_examples.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  automake bison boost-devel

# from epel
BuildRequires:  graphviz

# from aegisco
# repofile: http://rpm.aegisco.com/aegisco/$dist/aegisco.repo
BuildRequires:  flex >= 2.5.33

# gecode requires gcc 4.2 or higher
%if 0%{?rhel} == 5
BuildRequires:  gcc44 gcc44-c++
%else
BuildRequires:  gcc gcc-c++
%endif

# for documentation
BuildRequires:  doxygen

%description
Gecode is a toolkit for developing constraint-based systems and
applications. Gecode provides a constraint solver with state-of-the-art
performance while being modular and extensible.


%package devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package doc
Summary:        Documentation for %{name}
Group:          Documentation
Requires:       %{name} = %{version}-%{release}
%if 0%{?fedora} >= 10 || 0%{?rhel} >= 6
BuildArch: noarch
%endif

%description doc
The %{name}-doc package contains documentation files for %{name}.


%package examples
Summary:        Example code for %{name}
Group:          Documentation
Requires:       %{name} = %{version}-%{release}
%if 0%{?fedora} >= 10 || 0%{?rhel} >= 6
BuildArch: noarch
%endif

%description examples
The %{name}-examples package contains example code for %{name}.


%prep
%setup -q
%patch0 -p1 -b .no_examples

# Fix permissions
find . -name '*.hh' -o -name '*.hpp' -o -name '*.cpp' -exec chmod 0644 '{}' \;
chmod 0644 LICENSE misc/doxygen/*.png

# Fix encoding
pushd examples
for file in black-hole.cpp scowl.hpp word-square.cpp; do
    iconv -f ISO-8859-1 -t UTF-8 -o $file.new $file && \
    touch -r $file $file.new && \
    mv $file.new $file
done
popd


%build
aclocal
autoconf

%configure \
%if 0%{?rhel} == 5
  CC=gcc44 CXX=g++44 \
%endif
  --disable-examples \
  --enable-float-vars \
  --with-boost-include=/usr/include/boost \
	--disable-gist \
  --disable-qt

make %{?_smp_mflags}
make doc
make ChangeLog

iconv --from=ISO-8859-1 --to=UTF-8 -o ChangeLog.new ChangeLog
mv ChangeLog.new ChangeLog


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

#move docs and examples to build root
mkdir -p ${RPM_BUILD_ROOT}%{_defaultdocdir}/%{name}-doc-%{version}
mv doc/html ${RPM_BUILD_ROOT}%{_defaultdocdir}/%{name}-doc-%{version}


%clean
rm -rf $RPM_BUILD_ROOT


%post -p /sbin/ldconfig


%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc ChangeLog LICENSE
%{_libdir}/*.so.*

%files devel
%defattr(-,root,root,-)
%{_bindir}/fz
%{_datadir}/%{name}
%{_includedir}/%{name}
%{_libdir}/*.so

%files doc
%defattr(-,root,root,-)
%{_defaultdocdir}/%{name}-doc-%{version}/html

%files examples
%defattr(-,root,root,-)
%doc examples/*


%changelog
* Fri Apr 01 2011 Erik Sabowski and James Sulinski <team@aegisco.com> 3.5.0-1
- Update for gecode-3.5.0
- Disabled "gist" and "qt" configure options

* Sat May  8 2010 ELMORABITY Mohamed <melmorabity@fedoraproject.org> 3.3.1-1
- Initial RPM release
