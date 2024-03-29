%define _unpackaged_files_terminate_build 1
%define rname icinga2-usersyncd

Name: python3-module-%rname
Version: 0.1.0
Release: alt1

Group: Monitoring
Summary: A daemon to synchronize ApiUser entries with Host agents on an Icinga 2 instance
Url: http://git.altlinux.org/people/manowar/packages/icinga2-usersyncd.git
License: GPLv2+

BuildArch: noarch

Source: %name-%version.tar

BuildRequires(pre): rpm-build-python3
BuildRequires: python3(setuptools) python3(wheel) python3(pytest)
BuildRequires: python3(icinga2apic)

%description
A daemon to synchronize ApiUser entries with Host agents on an
Icinga 2 instance.

%prep
%setup

%build
%pyproject_build

%install
%pyproject_install

%files
%python3_sitelibdir_noarch/%rname
%python3_sitelibdir_noarch/%rname-%version.dist-info

%changelog
