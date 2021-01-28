%global scl_name_prefix rh-
%global scl_name_base ruby
%global scl_name_version 30

# Do not produce empty debuginfo package.
%global debug_package %{nil}

# Support SCL over NFS.
%global nfsmountable 1

# nfsmountable macro must be defined before defining the %%scl_package macro
%global scl %{scl_name_prefix}%{scl_name_base}%{scl_name_version}
%scl_package %scl

%{!?install_scl: %global install_scl 1}

Summary: Package that installs %scl
Name: %scl_name
Version: 3.7
Release: 1%{?dist}
License: GPLv2+
Source0: README
Source1: LICENSE
%if 0%{?install_scl}
Requires: %{scl_prefix}ruby
%endif
BuildRequires: help2man
BuildRequires: scl-utils-build

%description
This is the main package for %scl Software Collection.

%package runtime
Summary: Package that handles %scl Software Collection.
Requires: scl-utils

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary: Package shipping basic build configuration
Requires: scl-utils-build

%description build
Package shipping essential configuration macros to build %scl Software Collection.

%package scldevel
Summary: Package shipping development files for %scl

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.

%prep
%setup -T -c

# Expand macros used in README file.
cat > README << EOF
%{expand:%(cat %{SOURCE0})}
EOF

cp %{SOURCE1} .

%build
# Generate a helper script that will be used by help2man.
cat > h2m_help << 'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_help

# Generate the man page from include.h2m and ./h2m_help --help output.
help2man -N --section 7 ./h2m_help -o %{scl_name}.7

%install
%scl_install

# Fix: install gem binaries to SCL PATH
# https://bugzilla.redhat.com/show_bug.cgi?id=1225496
perl -e 'while (<>) { if (/^([^=]*=["'\'']?)([^\$]*)(.*)/) { $pre = $1 ; $path = $2 ;
  $post = $3 ; ($newpath = $path) =~ s/usr/usr\/local/ ; $newpath =~ s/://g ;
  print "$pre$newpath:$path$post\n" }}' <<EOF >>%{buildroot}%{_scl_scripts}/enable
export PATH=%{_bindir}\${PATH:+:\${PATH}}
export LD_LIBRARY_PATH=%{_libdir}\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}
export MANPATH=%{_mandir}:\$MANPATH
export PKG_CONFIG_PATH=%{_libdir}/pkgconfig\${PKG_CONFIG_PATH:+:\${PKG_CONFIG_PATH}}
# For SystemTap.
export XDG_DATA_DIRS=%{_datadir}:\${XDG_DATA_DIRS:-/usr/local/share:/usr/share}
EOF

cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel << EOF
%%scl_%{scl_name_base} %{scl}
%%scl_prefix_%{scl_name_base} %{scl_prefix}
EOF

# Install generated man page.
mkdir -p %{buildroot}%{_mandir}/man7/
install -p -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/

# Create directory for pkgconfig files, originally provided by pkgconfig
# package, but not for SCL.
mkdir -p %{buildroot}%{_libdir}/pkgconfig

# Create directory for license files (rhbz#1420233).
%{?_licensedir:mkdir -p %{buildroot}%{_licensedir}}

%files

%files runtime
%doc README LICENSE
%scl_files
%{?_licensedir:%dir %{_licensedir}}
# Own the manual directories (rhbz#1073458, rhbz#1072319).
%dir %{_mandir}/man1
%dir %{_mandir}/man5
%dir %{_mandir}/man7
%dir %{_libdir}/pkgconfig
%{_mandir}/man7/%{scl_name}.*

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Wed Dec 16 2020 Jun Aruga <jaruga@redhat.com> - 3.7-1
- Update to 3.0.
  Resolves: rhbz#1903661

* Thu Jan 30 2020 Jun Aruga <jaruga@redhat.com> - 2.7-2
- Update to 2.7.

* Mon Jan 07 2019 Vít Ondruch <vondruch@redhat.com> - 2.6-1
- Update to 2.6.

* Fri Jan 05 2018 Jun Aruga <jaruga@redhat.com> - 2.5-2
- Update to 2.5.

* Tue Feb 28 2017 Vít Ondruch <vondruch@redhat.com> - 2.4-2
- Own the license directory.
  Resolves: rhbz#1420233

* Tue Dec 13 2016 Vít Ondruch <vondruch@redhat.com> - 2.4-1
- Initial package
