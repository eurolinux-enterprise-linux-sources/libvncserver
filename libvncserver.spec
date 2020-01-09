
# Fedora pkg review: http://bugzilla.redhat.com/429749

%if 0%{?fedora}
%define system_minilzo 1
%endif

Summary: Library to make writing a vnc server easy
Name:    libvncserver
Version: 0.9.7
Release: 7%{?dist}.1
# NOTE: --with-tightvnc-filetransfer => GPLv2
License: GPLv2+
Group:   System Environment/Libraries
URL:     http://libvncserver.sourceforge.net/
# This source is made from
# http://downloads.sf.net/libvncserver/LibVNCServer-%{version}.tar.gz
# by deleting all .jar files.
Source0:  LibVNCServer-%{version}-clean.tar.xz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Patch1: libvncserver-0.9.7-system_minilzo.patch
Patch2: libvncserver-0.9.1-multilib.patch

# safer LINUX platform detection (from opensuse)
Patch50:  libvncserver-LINUX.patch

## upstream patches
Patch100: libvncserver-0.9.1-close_server_socket.patch

# Fix CVE-2014-6051, bug #1184538
Patch101: LibVNCServer-0.9.10-CVE-2014-6051.patch

# Fix CVE-2014-6055, bug #1184538
Patch102: LibVNCServer-0.9.10-CVE-2014-6055.patch

# upstream name
Obsoletes: LibVNCServer < 0.9.1
Provides:  LibVNCServer = %{version}-%{release}

BuildRequires: libjpeg-devel
BuildRequires: zlib-devel
%{?system_minilzo:BuildRequires: lzo-minilzo lzo-devel}

%description
LibVNCServer makes writing a VNC server (or more correctly, a program
exporting a framebuffer via the Remote Frame Buffer protocol) easy.

It hides the programmer from the tedious task of managing clients and
compression schemata.

%package devel
Summary: Development files for %{name}
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
# libvncserver-config deps
Requires: coreutils
# upstream name
#Obsoletes: LibVNCServer-devel < %{version}-%{release}
Provides:  LibVNCServer-devel = %{version}-%{release}
%description devel
%{summary}.


%prep
%setup -q -n LibVNCServer-%{version}

%if 0%{?system_minilzo}
%patch1 -p1 -b .system_minilzo
#nuke bundled minilzo
find . -name minilzo\* -exec rm -f {} \;
%endif

%patch2 -p1 -b .multilib
%patch50 -p0 -b .LINUX
%patch100 -p1 -b .close_server_socket
%patch101 -p1
%patch102 -p1

# fix encoding
mv AUTHORS AUTHORS.OLD && \
iconv -f ISO_8859-1 -t UTF8 AUTHORS.OLD > AUTHORS && \
touch --reference AUTHORS.OLD AUTHORS

# fix source perms
find -name "*.c" -o -name "*.h" | xargs chmod 644


%build
%configure \
  --disable-static \
  --without-tightvnc-filetransfer

# hack to omit unused-direct-shlib-dependencies
sed -i -e 's! -shared ! -Wl,--as-needed\0!g' libtool

make %{?_smp_mflags} %{?system_minilzo:CFLAGS="$RPM_OPT_FLAGS -I %{_includedir}/lzo" LDFLAGS="$LDFLAGS -lminilzo"}


%install
rm -rf %{buildroot}

make install DESTDIR=%{buildroot}

# unpackaged files
rm -f %{buildroot}%{_bindir}/LinuxVNC
rm -f %{buildroot}%{_libdir}/lib*.a
rm -f %{buildroot}%{_libdir}/lib*.la


%clean
rm -rf %{buildroot}


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README TODO
%{_libdir}/libvncclient.so.0*
%{_libdir}/libvncserver.so.0*

%files devel
%defattr(-,root,root,-)
%{_bindir}/*-config
%{_includedir}/rfb/
%{_libdir}/libvncclient.so
%{_libdir}/libvncserver.so


%changelog
* Fri Jan 23 2015 Petr Pisar <ppisar@redhat.com> - 0.9.7-7.1
- Fix CVE-2014-6051 (integer overflow in screen size handling) (bug #1184538)
- Fix CVE-2014-6055 (server stacked-based buffer overflow in file transfer
  handling) (bug #1184538)

* Fri May 06 2011 Petr Pisar <ppisar@redhat.com> - 0.9.7-7
- Revert CVE-2011-0904 and CVE-2011-0905 patch because libvncserver is not
  vulnerable (bug #696767)

* Wed Apr 27 2011 Petr Pisar <ppisar@redhat.com> - 0.9.7-6
- Fix CVE-2011-0904 and CVE-2011-0905 in more generic way (bug #696767)

* Wed Apr 20 2011 Petr Pisar <ppisar@redhat.com> - 0.9.7-5
- Fix CVE-2011-0904 (bug #696767)
- Fix CVE-2011-0905 (bug #696767)

* Thu Feb 18 2010 Stepan Kasal <skasal@redhat.com> - 0.9.7-4
- repack the tarball, there are .jar files without any source
- do not BR findutils, they are guaranteed in Fedora mock
- fix obsolete, so that it covers only packages created before this
  spec was added to Fedora

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 0.9.7-3.1
- Rebuilt for RHEL 6

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sat May 23 2009 Rex Dieter <rdieter@fedoraproject.org> - 0.9.7-3
- Socket is not closed when disconnecting from server (#501895)

* Mon May 04 2009 Rex Dieter <rdieter@fedoraproject.org> - 0.9.7-2
- fix detection of LINUX platform/define

* Mon May 04 2009 Rex Dieter <rdieter@fedoraproject.org> - 0.9.7-1
- LibVNCServer-0.9.7

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Apr 10 2008 Manuel Wolfshant <wolfy@fedoraproject.org> 0.9.1-3
- do not use bundled copy of minilzo (#439979)

* Sun Jan 27 2008 Rex Dieter <rdieter@fedoraproject.org> 0.9.1-2
- hack libtool to omit unused shlib dependencies
- fix AUTHORS encoding
- fix src perms

* Mon Jan 21 2008 Rex Dieter <rdieter@fedoraproject.org> 0.9.1-1
- 0.9.1
