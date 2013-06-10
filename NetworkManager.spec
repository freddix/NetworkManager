%define		gitver	%{nil}

Summary:	Network Manager for GNOME
Name:		NetworkManager
Version:	0.9.8.2
%if "%{gitver}" != "%{nil}"
Release:	0.%{gitver}.1
%else
Release:	1
%endif
License:	GPL v2
Group:		Daemons
%if "%{gitver}" != "%{nil}"
Source0:	http://cgit.freedesktop.org/NetworkManager/NetworkManager/snapshot/%{name}-%{gitver}.tar.bz2
# Source0-md5:	7ac4ee1652e77ba064a5e18dc7af7e25
%else
Source0:	ftp://ftp.gnome.org/pub/GNOME/sources/NetworkManager/0.9/%{name}-%{version}.tar.xz
# Source0-md5:	7ac4ee1652e77ba064a5e18dc7af7e25
%endif
Source1:	%{name}-nm-system-settings.conf
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	dbus-glib-devel
BuildRequires:	gettext-devel
BuildRequires:	gobject-introspection-devel
BuildRequires:	intltool
BuildRequires:	libgcrypt-devel
BuildRequires:	libnl-devel
BuildRequires:	libtool
BuildRequires:	pkg-config
BuildRequires:	polkit-devel
BuildRequires:	ppp-devel
BuildRequires:	udev-glib-devel
BuildRequires:	wireless-tools-devel
Requires(post,preun,postun):	systemd-units
Requires:	%{name}-libs = %{version}-%{release}
Requires:	dhcpcd
Suggests:	crda
Suggests:	wpa_supplicant
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libexecdir	%{_libdir}/%{name}

%description
Network Manager for GNOME.

%package autoipd
Summary:	Network Manager autoipd plugin
Group:		Networking
Requires:	%{name} = %{version}-%{release}
Requires:	avahi-autoipd

%description autoipd
Network Manager autoipd plugin.

%package modem
Summary:	Network Manager modem plugin
Group:		Networking
Requires:	%{name} = %{version}-%{release}
Requires:	udev

%description modem
Network Manager modem plugin.

%package ppp
Summary:	Network Manager PPP plugin
Group:		Networking
Requires:	%{name} = %{version}-%{release}
Requires:	ppp

%description ppp
Network Manager PPP plugin.

%package libs
Summary:	Network Manager shared libraries
Group:		X11/Libraries

%description libs
Network Manager shared libraries.

%package devel
Summary:	Network Manager includes and more
Group:		X11/Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Network Manager includes and more.

%package apidocs
Summary:	NetworkManager API documentation
Group:		Documentation
Requires:	gtk-doc-common

%description apidocs
NetworkManager API documentation.

%prep
%if "%{gitver}" != "%{nil}"
%setup -qn %{name}-%{gitver}
%else
%setup -qn %{name}-%{version}
%endif

%build
%{__gtkdocize}
%{__intltoolize}
%{__libtoolize}
%{__aclocal} -I m4
%{__autoheader}
%{__autoconf}
%{__automake}
%configure \
	--disable-silent-rules			\
	--disable-static			\
	--enable-more-warnings=no		\
	--with-crypto=gnutls			\
	--with-dhcpcd=/usr/sbin/dhcpcd		\
	--with-distro=generic			\
	--with-html-dir=%{_gtkdocdir}		\
	--with-iptables=/usr/sbin/iptables	\
	--with-system-ca-path=/etc/certs	\
	--with-systemdsystemunitdir=%{systemdunitdir}	\
	--with-session-tracking=systemd
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/%{name}/{VPN,dispatcher.d,system-connections},%{_datadir}/gnome-vpn-properties}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/nm-system-settings.conf

# Cleanup
rm -f $RPM_BUILD_ROOT%{_libexecdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/pppd/*/*.la

%find_lang %{name} --with-gnome --all-name

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post NetworkManager.service

%preun
%systemd_preun NetworkManager.service

%postun
%systemd_postun

%post	libs -p /usr/sbin/ldconfig
%postun	libs -p /usr/sbin/ldconfig

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README TODO
%attr(755,root,root) %{_bindir}/nm-online
%attr(755,root,root) %{_bindir}/nm-tool
%attr(755,root,root) %{_bindir}/nmcli
%attr(755,root,root) %{_libexecdir}/nm-dhcp-client.action
%attr(755,root,root) %{_libexecdir}/nm-dispatcher.action
%attr(755,root,root) %{_sbindir}/NetworkManager
%{systemdunitdir}/NetworkManager-dispatcher.service
%{systemdunitdir}/NetworkManager-wait-online.service
%{systemdunitdir}/NetworkManager.service

%dir %{_datadir}/gnome-vpn-properties
%dir %{_libexecdir}
%dir %{_sysconfdir}/NetworkManager
%dir %{_sysconfdir}/NetworkManager/VPN
%dir %{_sysconfdir}/NetworkManager/dispatcher.d
%dir %{_sysconfdir}/NetworkManager/system-connections

%{_mandir}/man1/nm-online.1*
%{_mandir}/man1/nm-tool.1*
%{_mandir}/man1/nmcli.1*
%{_mandir}/man5/NetworkManager.conf.5*
%{_mandir}/man5/nm-system-settings.conf.5*
%{_mandir}/man8/NetworkManager.8*

%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/NetworkManager/nm-system-settings.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.NetworkManager.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dbus-1/system.d/nm-dhcp-client.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dbus-1/system.d/nm-dispatcher.conf
%{_datadir}/dbus-1/system-services/org.freedesktop.NetworkManager.service
%{_datadir}/dbus-1/system-services/org.freedesktop.nm_dispatcher.service
%{_datadir}/polkit-1/actions/org.freedesktop.NetworkManager.policy

%files autoipd
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dbus-1/system.d/nm-avahi-autoipd.conf
%attr(755,root,root) %{_libexecdir}/nm-avahi-autoipd.action

%files ppp
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/pppd/*/nm-pppd-plugin.so

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %ghost %{_libdir}/libnm-util.so.?
%attr(755,root,root) %ghost %{_libdir}/libnm-glib.so.?
%attr(755,root,root) %ghost %{_libdir}/libnm-glib-vpn.so.?
%attr(755,root,root) %{_libdir}/libnm-util.so.*.*.*
%attr(755,root,root) %{_libdir}/libnm-glib.so.*.*.*
%attr(755,root,root) %{_libdir}/libnm-glib-vpn.so.*.*.*
%{_libdir}/girepository-1.0/*.typelib

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libnm-util.so
%attr(755,root,root) %{_libdir}/libnm-glib.so
%attr(755,root,root) %{_libdir}/libnm-glib-vpn.so
%{_libdir}/libnm-util.la
%{_libdir}/libnm-glib.la
%{_libdir}/libnm-glib-vpn.la
%{_includedir}/NetworkManager
%{_includedir}/libnm-glib
%{_pkgconfigdir}/NetworkManager.pc
%{_pkgconfigdir}/libnm-util.pc
%{_pkgconfigdir}/libnm-glib.pc
%{_pkgconfigdir}/libnm-glib-vpn.pc
%{_datadir}/gir-1.0/*.gir
%{_datadir}/vala/vapi/*.deps
%{_datadir}/vala/vapi/*.vapi

%files apidocs
%defattr(644,root,root,755)
%{_gtkdocdir}/NetworkManager
%{_gtkdocdir}/libnm-glib
%{_gtkdocdir}/libnm-util

