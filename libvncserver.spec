
%if 0%{?fedora} || 0%{?rhel} > 5
%define system_minilzo 1
%endif

Summary: Library to make writing a vnc server easy
Name:    libvncserver
Version: 0.9.9
Release: 11%{?dist}
# NOTE: --with-tightvnc-filetransfer => GPLv2
License: GPLv2+
Group:   System Environment/Libraries
URL:     http://libvncserver.sourceforge.net/
Source0: http://downloads.sf.net/libvncserver/LibVNCServer-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# workaround there being no x11vnc/ dir in tarball
Patch0: LibVNCServer-0.9.9-no_x11vnc.patch
Patch1: LibVNCServer-0.9.9-system_minilzo.patch
Patch2: libvncserver-0.9.1-multilib.patch
# pkgconfig love (upstreamable)
Patch3: LibVNCServer-0.9.9-pkgconfig.patch
# Fix CVE-2014-6051, bug #1157671
Patch4: LibVNCServer-0.9.10-CVE-2014-6051.patch
# Fix CVE-2014-6052, bug #1157671
Patch5: LibVNCServer-0.9.9-CVE-2014-6052.patch
# Fix CVE-2014-6053, bug #1157671
Patch6: LibVNCServer-0.9.10-CVE-2014-6053.patch
# Fix CVE-2014-6054, bug #1157671
Patch7: LibVNCServer-0.9.10-CVE-2014-6054.patch
# Fix CVE-2014-6055, bug #1157671
Patch8: LibVNCServer-0.9.10-CVE-2014-6055.patch
# Fix a crash in the VNC server library on connecting an IPv4 client if the
# server could not start listening on an IPv6 socket, bug #1314814, in upstream
# after 0.9.9,
# <https://sourceforge.net/p/libvncserver/mailman/message/29358128/>
Patch9: LibVNCServer-0.9.9-libvncserver-sockets.c-do-not-segfault-when-listenSo.patch

# upstream name
Obsoletes: LibVNCServer < 0.9.1
Provides:  LibVNCServer = %{version}-%{release}

BuildRequires: automake autoconf
BuildRequires: libgcrypt-devel
BuildRequires: libjpeg-devel
%{?system_minilzo:BuildRequires: lzo-minilzo lzo-devel}
BuildRequires: pkgconfig(gnutls)
# for %%check
BuildRequires: xorg-x11-server-Xvfb
BuildRequires: xorg-x11-xauth
BuildRequires: zlib-devel

%description
LibVNCServer makes writing a VNC server (or more correctly, a program
exporting a framebuffer via the Remote Frame Buffer protocol) easy.

It hides the programmer from the tedious task of managing clients and
compression schemata.

%package devel
Summary: Development files for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
# libvncserver-config deps
Requires: coreutils
# upstream name
#Obsoletes: LibVNCServer-devel < %{version}-%{release}
Provides:  LibVNCServer-devel = %{version}-%{release}
%description devel
%{summary}.


%prep
%setup -q -n LibVNCServer-%{version}

%patch0 -p1 -b .no_x11vnc
%if 0%{?system_minilzo}
%patch1 -p1 -b .system_minilzo
#nuke bundled minilzo
rm -f common/lzodefs.h common/lzoconf.h commmon/minilzo.h common/minilzo.c
%endif
%patch2 -p1 -b .multilib
%patch3 -p1 -b .pkgconfig
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1

# fix encoding
for file in AUTHORS ChangeLog ; do
mv ${file} ${file}.OLD && \
iconv -f ISO_8859-1 -t UTF8 ${file}.OLD > ${file} && \
touch --reference ${file}.OLD $file 
done

# needed by patch 1 (and to nuke rpath's)
autoreconf


%build
%configure \
  --disable-static \
  --without-tightvnc-filetransfer \
  --with-gcrypt \
  --without-png

# hack to omit unused-direct-shlib-dependencies
sed -i -e 's! -shared ! -Wl,--as-needed\0!g' libtool

make V=1 %{?_smp_mflags}


%install
rm -rf %{buildroot}

make install DESTDIR=%{buildroot}

# unpackaged files
rm -fv %{buildroot}%{_bindir}/linuxvnc
rm -fv %{buildroot}%{_libdir}/lib*.a
rm -fv %{buildroot}%{_libdir}/lib*.la


%check
unset DISPLAY
# Run a fake X session 
# rawhide/koji seems to have some some unreproducible errors atm -- rex
# there's also selinux :( https://bugzilla.redhat.com/843603
xvfb-run -a make -C test test ||:


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
%{_bindir}/libvncserver-config
%{_includedir}/rfb/
%{_libdir}/libvncclient.so
%{_libdir}/libvncserver.so
%{_libdir}/pkgconfig/libvncclient.pc
%{_libdir}/pkgconfig/libvncserver.pc


%changelog
* Fri Sep 15 2017 Petr Pisar <ppisar@redhat.com> - 0.9.9-11
- Fix a crash in the VNC server library on connecting an IPv4 client if the
  server could not start listening on an IPv6 socket (bug #1314814)

* Fri Oct 31 2014 Petr Pisar <ppisar@redhat.com> - 0.9.9-10
- Fix CVE-2014-6051 (integer overflow in screen size handling) (bug #1157671)
- Fix CVE-2014-6052 (NULL pointer dereference in framebuffer setup)
  (bug #1157671)
- Fix CVE-2014-6053 (NULL pointer dereference in ClientCutText message
  handling) (bug #1157671)
- Fix CVE-2014-6054 (server divide-by-zero in scaling factor handling)
  (bug #1157671)
- Fix CVE-2014-6055 (server stacked-based buffer overflow in file transfer
  handling) (bug #1157671)

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 0.9.9-9
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 0.9.9-8
- Mass rebuild 2013-12-27

* Tue Jul 23 2013 Petr Pisar <ppisar@redhat.com> - 0.9.9-7.2
- Specify dependencies on libpng and libgcrypt (bug #852660)

* Mon Apr 08 2013 Daniel Mach <dmach@redhat.com> - 0.9.9-7.1
- Rebuild for gnutls

* Thu Feb 14 2013 Rex Dieter <rdieter@fedoraproject.org> 0.9.9-7
- pkgconfig love (#854111)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.9-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jan 18 2013 Adam Tkac <atkac redhat com> - 0.9.9-5
- rebuild due to "jpeg8-ABI" feature drop

* Fri Dec 21 2012 Adam Tkac <atkac redhat com> - 0.9.9-4
- rebuild against new libjpeg

* Thu Jul 26 2012 Rex Dieter <rdieter@fedoraproject.org> 0.9.9-3
- libvncserver fails to build in mock with selinux enabled (#843603)

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon May 07 2012 Rex Dieter <rdieter@fedoraproject.org> 0.9.9-1
- 0.9.9

* Wed Apr 18 2012 Petr Pisar <ppisar@redhat.com> 0.9.8.2-4
- Enable system lzo library on rhel >= 6 (#813764)

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.8.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sat Dec 31 2011 Christoph Wickert <cwickert@fedoraproject.org> - 0.9.8.2-2
- On F15, %%check needs xorg-x11-xauth, too

* Tue Dec 13 2011 Rex Dieter <rdieter@fedoraproject.org> 0.9.8.2-1
- 0.9.8.2 (#694975)
- new %%check section (yay for xvfb-run)

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.7-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Feb 18 2010 Stepan Kasal <skasal@redhat.com> - 0.9.7-4
- repack the tarball, there are .jar files without any source
- do not BR findutils, they are guaranteed in Fedora mock
- fix obsolete, so that it covers only packages created before this
  spec was added to Fedora

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
