Summary: The exim mail transfer agent
Name: exim
Version: 4.54
Release: 4%{?dist}
License: GPL
Url: http://www.exim.org/
Group: System Environment/Daemons
Buildroot: %{_tmppath}/%{name}-build.root
Provides: MTA smtpd smtpdaemon /usr/bin/newaliases
Provides: /usr/sbin/sendmail /usr/bin/mailq /usr/bin/rmail
PreReq: /sbin/chkconfig
PreReq: /sbin/service
PreReq: %{_sbindir}/alternatives
PreReq: %{_sbindir}/groupadd, %{_sbindir}/useradd
Source: ftp://ftp.exim.org/pub/exim/exim4/exim-%{version}.tar.bz2
Source2: exim.init
Source3: exim.sysconfig
Source4: exim.logrotate
Source11: exim.pam
Source13: http://marc.merlins.org/linux/exim/files/sa-exim-4.2.tar.gz
Patch4: exim-rhl.patch
Patch6: exim-4.50-config.patch
Patch8: exim-4.24-libdir.patch
Patch12: exim-4.33-cyrus.patch
Patch13: exim-4.43-pamconfig.patch
Patch14: exim-4.50-spamdconf.patch
Patch15: exim-4.52-dynamic-pcre.patch

Requires: /etc/aliases
BuildRequires: db4-devel openssl-devel openldap-devel pam-devel
BuildRequires: lynx pcre-devel sqlite-devel
BuildRequires: cyrus-sasl-devel openldap-devel openssl-devel mysql-devel postgresql-devel
BuildRequires: libXaw-devel libXmu-devel libXext-devel libX11-devel libSM-devel libICE-devel libXpm-devel
PreReq: cyrus-sasl openldap openssl

%description
Exim is a mail transport agent (MTA) developed at the University of
Cambridge for use on Unix systems connected to the Internet. In style
it is similar to Smail 3, but its facilities are more extensive, and
in particular it has options for verifying incoming sender and
recipient addresses, for refusing mail from specified hosts, networks,
or senders, and for controlling mail relaying. Exim is in production
use at quite a few sites, some of which move hundreds of thousands of
messages per day.

%package mon
Summary: X11 monitor application for exim
Group: Applications/System
License: Free

%description mon
The Exim Monitor is an optional supplement to the Exim package. It
displays information about Exim's processing in an X window, and an
administrator can perform a number of control actions from the window
interface.

%package sa
Summary: Exim SpamAssassin at SMTP time - d/l plugin
Group: System Environment/Daemons
Requires: exim

%description sa
Allows running of SA on incoming mail and rejection at SMTP time as
well as other nasty things like teergrubing.

%prep
%setup -q
%setup -q -T -D -a 13
# patch sa
cat sa-exim*/localscan_dlopen_exim_4.20_or_better.patch | patch -p1 
cp src/EDITME Local/Makefile
cp exim_monitor/EDITME Local/eximon.conf

%patch4 -p1 -b .rhl
%patch6 -p1 -b .config
%patch8 -p1 -b .libdir
%patch12 -p1 -b .cyrus
%patch13 -p1 -b .pam
%patch14 -p1 -b .spamd
%patch15 -p1 -b .pcre

%build
%ifnarch s390 s390x
    make CFLAGS="$RPM_OPT_FLAGS -fpie" LFLAGS=-pie _lib=%{_lib}
%else
    make CFLAGS="$RPM_OPT_FLAGS -fPIE" LFLAGS=-pie _lib=%{_lib}
%endif

# build sa-exim
cd sa-exim*
perl -pi -e 's|\@lynx|HOME=/ /usr/bin/lynx|g;' Makefile
make SACONF=%{_sysconfdir}/exim/sa-exim.conf CFLAGS="$RPM_OPT_FLAGS -fPIC"


%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_sbindir}
mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_libdir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pam.d
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/exim

cd build-`scripts/os-type`-`scripts/arch-type`
install -m 4775 exim $RPM_BUILD_ROOT%{_sbindir}

for i in eximon eximon.bin exim_dumpdb exim_fixdb exim_tidydb \
	exinext exiwhat exim_dbmbuild exicyclog exim_lock \
	exigrep eximstats exipick exiqgrep exiqsumm \
	exim_checkaccess convert4r4
do
    install -m 0775 $i $RPM_BUILD_ROOT%{_sbindir}
done

cd ..

install -m 0644 src/configure.default $RPM_BUILD_ROOT%{_sysconfdir}/exim/exim.conf
install -m 0644 $RPM_SOURCE_DIR/exim.pam $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/exim

mkdir -p $RPM_BUILD_ROOT/usr/lib
pushd $RPM_BUILD_ROOT/usr/lib
ln -sf ../sbin/exim sendmail.exim
popd

pushd $RPM_BUILD_ROOT%{_sbindir}/
ln -sf exim sendmail.exim
popd

pushd $RPM_BUILD_ROOT%{_bindir}/
ln -sf ../sbin/exim mailq.exim
ln -sf ../sbin/exim runq.exim
ln -sf ../sbin/exim rsmtp.exim
ln -sf ../sbin/exim rmail.exim
ln -sf ../sbin/exim newaliases.exim
popd

install -d -m 0750 $RPM_BUILD_ROOT%{_var}/spool/exim
install -d -m 0750 $RPM_BUILD_ROOT%{_var}/spool/exim/db
install -d -m 0750 $RPM_BUILD_ROOT%{_var}/spool/exim/input
install -d -m 0750 $RPM_BUILD_ROOT%{_var}/spool/exim/msglog
install -d -m 0750 $RPM_BUILD_ROOT%{_var}/log/exim

mkdir -p $RPM_BUILD_ROOT%{_mandir}/man8
install -m644 doc/exim.8 $RPM_BUILD_ROOT%{_mandir}/man8/exim.8
pod2man --center=EXIM --section=8 \
       $RPM_BUILD_ROOT/usr/sbin/eximstats \
       $RPM_BUILD_ROOT%{_mandir}/man8/eximstats.8

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m 644 $RPM_SOURCE_DIR/exim.sysconfig $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/exim

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
install $RPM_SOURCE_DIR/exim.init $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/exim

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
install -m 0644 $RPM_SOURCE_DIR/exim.logrotate $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/exim

# install sa
cd sa-exim*
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}/exim
install *.so  $RPM_BUILD_ROOT%{_libexecdir}/exim
install -m 644 *.conf $RPM_BUILD_ROOT%{_sysconfdir}/exim
ln -s sa-exim*.so $RPM_BUILD_ROOT%{_libexecdir}/exim/sa-exim.so

# generate ghost .pem file
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/ssl/{certs,private}
touch $RPM_BUILD_ROOT/%{_datadir}/ssl/{certs,private}/exim.pem
chmod 600 $RPM_BUILD_ROOT/%{_datadir}/ssl/{certs,private}/exim.pem


%clean
rm -rf $RPM_BUILD_ROOT

%pre
%{_sbindir}/useradd -d %{_var}/spool/exim -s /sbin/nologin -G mail -M -r -u 93 exim 2>/dev/null
exit 0

%post
/sbin/chkconfig --add exim

%{_sbindir}/alternatives --install %{_sbindir}/sendmail mta %{_sbindir}/sendmail.exim 10 \
	--slave %{_bindir}/mailq mta-mailq %{_bindir}/mailq.exim \
	--slave %{_bindir}/runq mta-runq %{_bindir}/runq.exim \
	--slave %{_bindir}/rsmtp mta-rsmtp %{_bindir}/rsmtp.exim \
	--slave %{_bindir}/rmail mta-rmail %{_bindir}/rmail.exim \
	--slave /etc/pam.d/smtp mta-pam /etc/pam.d/exim \
	--slave %{_bindir}/newaliases mta-newaliases %{_bindir}/newaliases.exim \
	--slave /usr/lib/sendmail mta-sendmail /usr/lib/sendmail.exim \
	--slave %{_mandir}/man1/mailq.1.gz mta-mailqman %{_mandir}/man8/exim.8.gz \
	--initscript exim

if [ ! -f %{_datadir}/ssl/certs/exim.pem ] ; then
  umask 077
  FQDN=`hostname`
  if [ "x${FQDN}" = "x" ]; then
    FQDN=localhost.localdomain
  fi
  cat << EOF | openssl req -new -x509 -days 365 -nodes -out %{_datadir}/ssl/certs/exim.pem -keyout %{_datadir}/ssl/private/exim.pem &>/dev/null
--
SomeState
SomeCity
SomeOrganization
SomeOrganizationalUnit
${FQDN}
root@${FQDN}
EOF
chown exim.exim %{_datadir}/ssl/{private,certs}/exim.pem
chmod 600 %{_datadir}/ssl/{private,certs}/exim.pem
fi

%preun
if [ $1 = 0 ]; then
	/sbin/service exim stop > /dev/null 2>&1
	/sbin/chkconfig --del exim
	%{_sbindir}/alternatives --remove mta %{_sbindir}/sendmail.exim
fi

%postun
if [ "$1" -ge "1" ]; then
	/sbin/service exim  condrestart > /dev/null 2>&1
        mta=`readlink /etc/alternatives/mta`
        if [ "$mta" == "%{_sbindir}/sendmail.exim" ]; then
                /usr/sbin/alternatives --set mta %{_sbindir}/sendmail.exim
        fi
fi

%files
%defattr(-,root,root)
%attr(4755,root,root) %{_sbindir}/exim
%{_sbindir}/exim_dumpdb
%{_sbindir}/exim_fixdb
%{_sbindir}/exim_tidydb
%{_sbindir}/exinext
%{_sbindir}/exiwhat
%{_sbindir}/exim_dbmbuild
%{_sbindir}/exicyclog
%{_sbindir}/exigrep
%{_sbindir}/eximstats
%{_sbindir}/exipick
%{_sbindir}/exiqgrep
%{_sbindir}/exiqsumm
%{_sbindir}/exim_lock
%{_sbindir}/exim_checkaccess
%{_sbindir}/convert4r4
%{_sbindir}/sendmail.exim
%{_bindir}/mailq.exim
%{_bindir}/runq.exim
%{_bindir}/rsmtp.exim
%{_bindir}/rmail.exim
%{_bindir}/newaliases.exim
/usr/lib/sendmail.exim
%{_mandir}/*/*

%defattr(-,exim,exim)
%dir %{_var}/spool/exim
%dir %{_var}/spool/exim/db
%dir %{_var}/spool/exim/input
%dir %{_var}/spool/exim/msglog
%dir %{_var}/log/exim

%defattr(-,root,mail)
%config(noreplace) %{_sysconfdir}/exim/exim.conf

%defattr(-,root,root)
%config %{_sysconfdir}/sysconfig/exim
%config %{_sysconfdir}/rc.d/init.d/exim
%config %{_sysconfdir}/logrotate.d/exim
%config %{_sysconfdir}/pam.d/exim

%doc ACKNOWLEDGMENTS LICENCE NOTICE README.UPDATING README 
%doc doc util/unknownuser.sh

%attr(0600,root,root) %ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_datadir}/ssl/certs/exim.pem
%attr(0600,root,root) %ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_datadir}/ssl/private/exim.pem

%files mon
%defattr(-,root,root)
%{_sbindir}/eximon
%{_sbindir}/eximon.bin

%files sa
%defattr(-,root,root)
%{_libexecdir}/exim
%config(noreplace) %{_sysconfdir}/exim/sa-*.conf
%doc sa-exim*/*.html
%doc sa-exim*/{ACKNOWLEDGEMENTS,INSTALL,LICENSE,TODO}

%changelog
* Sun Nov 13 2005 David Woodhouse <dwmw2@redhat.com> 4.54-4
- Fix 64-bit build

* Fri Nov 11 2005 David Woodhouse <dwmw2@redhat.com> 4.54-3
- Update X11 BuildRequires

* Wed Oct  5 2005 David Woodhouse <dwmw2@redhat.com> 4.54-2
- Rebuild for new OpenSSL
- Add MySQL and Postgres support to keep jgarzik happy

* Wed Oct  5 2005 David Woodhouse <dwmw2@redhat.com> 4.54-1
- Update to Exim 4.54
- Enable sqlite support

* Thu Aug 25 2005 David Woodhouse <dwmw2@redhat.com> 4.52-2
- Use system PCRE

* Fri Jul  1 2005 David Woodhouse <dwmw2@redhat.com> 4.52-1
- Update to Exim 4.52

* Thu Jun 16 2005 David Woodhouse <dwmw2@redhat.com> 4.51-3
- Rebuild for -devel

* Thu Jun 16 2005 David Woodhouse <dwmw2@redhat.com> 4.51-2
- Update CSA patch

* Wed May  4 2005 David Woodhouse <dwmw2@redhat.com> 4.51-1
- Update to Exim 4.51
- Include Tony's CSA support patch

* Tue Feb 22 2005 David Woodhouse <dwmw2@redhat.com> 4.50-2
- Move exim-doc into a separate package

* Tue Feb 22 2005 David Woodhouse <dwmw2@redhat.com> 4.50-1
- Update to Exim 4.50 and sa-exim 4.2
- Default headers_charset to utf-8
- Add sample spamd stuff to default configuration like exiscan-acl used to

* Sat Jan 15 2005 David Woodhouse <dwmw2@redhat.com> 4.44-1
- Update to Exim 4.44 and exiscan-acl-4.44-28

* Tue Jan  4 2005 David Woodhouse <dwmw2@redhat.com> 4.43-4
- Fix buffer overflows in host_aton() and SPA authentication

* Thu Dec 16 2004 David Woodhouse <dwmw2@redhat.com> 4.43-3
- Demonstrate SASL auth configuration in default config file
- Enable TLS and provide certificate if necessary
- Don't reject all GB2312 charset mail by default

* Mon Dec  6 2004 Thomas Woerner <twoerner@redhat.com> 4.43-2
- rebuild

* Thu Oct  7 2004 Thomas Woerner <twoerner@redhat.com> 4.43-1
- new version 4.43 with sasl support
- new exiscan-acl-4.43-28
- new config.samples and FAQ-html (added publication date)
- new BuildRequires for cyrus-sasl-devel openldap-devel openssl-devel
  and PreReq for cyrus-sasl openldap openssl

* Mon Sep 13 2004 Thomas Woerner <twoerner@redhat.com> 4.42-2
- update to sa-exim-4.1: fixes spamassassin's new score= string (#131796)

* Fri Aug 27 2004 Thomas Woerner <twoerner@redhat.com> 4.42-1
- new version 4.42

* Mon Aug  2 2004 Thomas Woerner <twoerner@redhat.com> 4.41-1
- new version 4.41

* Fri Jul  2 2004 Thomas Woerner <twoerner@redhat.com> 4.34-3
- added pre-definition of local_delivery using Cyrus-IMAP (#122912)
- added BuildRequires for pam-devel (#124555)
- fixed format string bugs (#125117)
- fixed sa-exim code placed wrong in spec file (#127102)
- extended postun with alternatives call

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed May 12 2004 David Woodhouse <dwmw2@redhat.com> 4.34-1
- Update to Exim 4.34, exiscan-acl 4.34-21

* Sat May 8 2004 David Woodhouse <dwmw2@redhat.com> 4.33-2
- fix buffer overflow in header_syntax check

* Wed May 5 2004 David Woodhouse <dwmw2@redhat.com> 4.33-1
- Update to Exim 4.33, exiscan-acl 4.33-20 to
  fix crashes both in exiscan-acl and Exim itself.

* Fri Apr 30 2004 David Woodhouse <dwmw2@redhat.com> 4.32-2
- Enable IPv6 support, Cyrus saslauthd support, iconv.

* Thu Apr 15 2004 David Woodhouse <dwmw2@redhat.com> 4.32-1
- update to Exim 4.32, exiscan-acl 4.32-17, sa-exim 4.0
- Fix Provides: and Source urls.
- include exiqgrep, exim_checkaccess, exipick
- require /etc/aliases instead of setup

* Tue Feb 24 2004 Thomas Woerner <twoerner@redhat.com> 4.30-6.1
- rebuilt

* Mon Feb 23 2004 Tim Waugh <twaugh@redhat.com>
- Use ':' instead of '.' as separator for chown.

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jan 27 2004 Thomas Woerner <twoerner@redhat.com> 4.30-5
- /usr/lib/sendmail is in alternatives, now
- /etc/alises is now in setup: new Requires for setup >= 2.5.31-1

* Tue Jan 13 2004 Thomas Woerner <twoerner@redhat.com> 4.30-4
- fixed group test in init script
- fixed config patch: use /etc/exim/exim.conf instead of /usr/exim/exim4.conf

* Wed Dec 10 2003 Nigel Metheringham <Nigel.Metheringham@InTechnology.co.uk> - 4.30-3
- Use exim.8 manpage from upstream
- Add eximstats.8 man page (from pod)
- Fixed mailq(1) man page alternatives links

* Mon Dec 08 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- do not package /etc/aliases. We currently require sendmail rpm until
  /etc/aliases moves into a more suitable rpm like "setup" or something else.

* Thu Dec  4 2003 Thomas Woerner <twoerner@redhat.com> 4.30-1
- new version 4.30
- new exiscan-acl-4.30-14
- disabled pie for s390 and s390x

* Wed Dec  3 2003 Tim Waugh <twaugh@redhat.com>
- Fixed PIE support to make it actually work.

* Wed Dec  3 2003 Thomas Woerner <twoerner@redhat.com> 4.24-1.2
- added -fPIE to CFLAGS

* Sat Nov 15 2003 Thomas Woerner <twoerner@redhat.com> 4.24-1.1
- fixed useradd in pre
- fixed alternatives in post

* Thu Nov 13 2003 Thomas Woerner <twoerner@redhat.com> 4.24-1
- new version 4.24 with LDAP and perl support
- added SpamAssassin sa plugin

* Mon Sep 23 2002 Bernhard Rosenkraenzer <bero@redhat.com> 3.36-1
- 3.36, fixes security bugs

* Thu Jun 21 2001 Tim Waugh <twaugh@redhat.com> 3.22-14
- Bump release number.

* Tue Jun 12 2001 Tim Waugh <twaugh@redhat.com> 3.22-13
- Remove pam-devel build dependency in order to share package between
  Guinness and Seawolf.

* Fri Jun  8 2001 Tim Waugh <twaugh@redhat.com> 3.22-12
- Fix format string bug.

* Wed May  2 2001 Tim Waugh <twaugh@redhat.com> 3.22-11
- SIGALRM patch from maintainer (bug #20908).
- There's no README.IPV6 any more (bug #32378).
- Fix logrotate entry for exim's pidfile scheme (bug #35436).
- ignore_target_hosts crash fix from maintainer.
- Make the summary start with a capital letter.
- Add reload entry to initscript; use $0 in strings.

* Sun Mar  4 2001 Tim Waugh <twaugh@redhat.com> 3.22-10
- Make sure db ownership is correct on upgrade, since we don't run as
  root when running as a daemon any more.

* Fri Mar  2 2001 Tim Powers <timp@redhat.com>
- rebuilt against openssl-0.9.6-1

* Sat Feb 17 2001 Tim Waugh <twaugh@redhat.com>
- Run as user mail, group mail when we drop privileges (bug #28193).

* Tue Feb 13 2001 Tim Powers <timp@redhat.com>
- added conflict with postfix

* Thu Jan 25 2001 Tim Waugh <twaugh@redhat.com>
- Avoid using zero-length salt in crypteq expansion.

* Tue Jan 23 2001 Tim Waugh <twaugh@redhat.com>
- Redo initscript internationalisation.
- Initscript uses bash not sh.

* Mon Jan 22 2001 Tim Waugh <twaugh@redhat.com>
- Okay, the real bug was in libident.

* Mon Jan 22 2001 Tim Waugh <twaugh@redhat.com>
- Revert the RST patch for now; if it's needed, it's a pidentd bug
  and should be fixed there.

* Mon Jan 22 2001 Tim Waugh <twaugh@redhat.com>
- 3.22.
- Build requires XFree86-devel.

* Mon Jan 15 2001 Tim Waugh <twaugh@redhat.com>
- New-style prereqs.
- Initscript internationalisation.

* Thu Jan 11 2001 Tim Waugh <twaugh@redhat.com>
- Security patch no longer required; 3.20 and later have a hide feature
  to do the same thing.
- Mark exim.conf noreplace.
- Better libident (RST) patch.

* Wed Jan 10 2001 Tim Waugh <twaugh@redhat.com>
- Fix eximconfig so that it tells the user the correct place to look
  for documentation
- Fix configure.default to deliver mail as group mail so that local
  delivery works

* Tue Jan 09 2001 Tim Waugh <twaugh@redhat.com>
- 3.21

* Mon Jan 08 2001 Tim Waugh <twaugh@redhat.com>
- Enable TLS support (bug #23196)

* Mon Jan 08 2001 Tim Waugh <twaugh@redhat.com>
- 3.20 (bug #21895).  Absorbs configure.default patch
- Put URLs in source tags where applicable
- Add build requirement on pam-devel

* Wed Oct 18 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Fix up eximconfig's header generation (we're not Debian), Bug #18068
- BuildRequires db2-devel (Bug #18089)
- Fix typo in logrotate script (Bug #18308)
- Local delivery must be setuid to work (Bug #18314)
- Don't send TCP RST packages to ident (Bug #19048)

* Wed Oct 18 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 3.16
- fix security bug
- some specfile cleanups
- fix handling of RPM_OPT_FLAGS

* Fri Aug 18 2000 Tim Powers <timp@redhat.com>
- fixed bug #16535, logrotate script changes

* Thu Aug 17 2000 Tim Powers <timp@redhat.com>
- fixed bug #16460
- fixed bug #16458
- fixed bug #16476

* Wed Aug 2 2000 Tim Powers <timp@redhat.com>
- fixed bug #15142

* Fri Jul 28 2000 Than Ngo <than@redhat.de>
- add missing restart function in startup script
- add rm -rf $RPM_BUILD_ROOT in install section
- use %%{_tmppath}

* Fri Jul 28 2000 Tim Powers <timp@redhat.com>
- fixed initscript so that condrestart doesn't return 1 when the test fails

* Mon Jul 24 2000 Prospector <prospector@redhat.com>
- rebuilt

* Mon Jul 17 2000 Tim Powers <timp@redhat.com>
- inits bakc to rc.d/init.d, using service to start inits

* Thu Jul 13 2000 Tim Powers <timp@redhat.com>
- applied patch from bug #13890

* Mon Jul 10 2000 Tim Powers <timp@redhat.com>
- rebuilt

* Thu Jul 06 2000 Tim Powers <timp@redhat.com>
- added patch submitted by <Chris.Keane@comlab.ox.ac.uk>, fixes bug #13539

* Thu Jul 06 2000 Tim Powers <timp@redhat.com>
- fixed broken prereq to require /etc/init.d

* Tue Jun 27 2000 Tim Powers <timp@redhat.com>
- PreReq initscripts >= 5.20

* Mon Jun 26 2000 Tim Powers <timp@redhat.com>
- fix init.d script location
- add condrestart to init.d script

* Wed Jun 14 2000 Nalin Dahyabhai <nalin@redhat.com>
- migrate to system-auth setup

* Tue Jun 6 2000 Tim Powers <timp@redhat.com>
- fixed man page location

* Tue May 9 2000 Tim Powers <timp@redhat.com>
- rebuilt for 7.0

* Fri Feb 04 2000 Tim Powers <timp@redhat.com>
- fixed the groups to be in Red Hat groups.
- removed Vendor header since it is going to be marked Red Hat in our build
	system.
- quiet setups
- strip binaries
- fixed so that man pages can be auto gzipped by new RPM (in files list
	/usr/man/*/* )
- built for Powertools 6.2

* Tue Jan 18 2000 Mark Bergsma <mark@mbergsma.demon.nl>
- Upgraded to exim 3.13
- Removed i386 specialization
- Added syslog support

* Wed Dec 8 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Upgraded to exim 3.12
- Procmail no longer used as the delivery agent

* Wed Dec 1 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Upgraded to exim 3.11

* Sat Nov 27 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added /etc/pam.d/exim

* Wed Nov 24 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Upgraded to exim 3.10

* Thu Nov 11 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added eximconfig script, thanks to Mark Baker
- Exim now uses the Berkeley DB library.

* Fri Aug 4 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Upgraded to version 3.03
- Removed version number out of the spec file name.

* Fri Jul 23 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added embedded Perl support.
- Added tcp_wrappers support.
- Added extra documentation in a new doc subpackage.

* Mon Jul 12 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added /usr/sbin/sendmail as a link to exim.
- Fixed wrong filenames in logrotate entry. 

* Sun Jul 11 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Now using the '%changelog' tag.
- Removed the SysV init links - let chkconfig handle them. 
- Replaced install -d with mkdir -p

* Sat Jul 10 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Fixed owner of the exim-mon files - the owner is now root

* Thu Jul 08 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Removed executable permission bits of /etc/exim.conf
- Removed setuid permission bits of all programs except exim
- Changed spool/log directory owner/groups to 'mail'
- Changed the default configuration file to make exim run
      as user and group 'mail'.

* Thu Jul 08 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added the /usr/bin/rmail -> /usr/sbin/exim symlink.
- Added the convert4r3 script.
- Added the transport-filter.pl script to the documentation.

* Thu Jul 08 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added procmail transport and director, and made that the
      default.
- Added the unknownuser.sh script to the documentation.

* Thu Jul 08 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added manpage for exim.
- Fixed symlinks pointing to targets under Buildroot.
- The exim logfiles will now only be removed when uninstalling,
      not upgrading.

* Wed Jul 07 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- Added 'Obsoletes' header.
- Added several symlinks to /usr/sbin/exim.

* Wed Jul 07 1999 Mark Bergsma <mark@mbergsma.demon.nl>
- First RPM packet release.
- Not tested on other architectures/OS'es than i386/Linux..
