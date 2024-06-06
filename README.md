`icinga2-usersyncd` is a daemon to synchronize ApiUser entries with
Host agents on an Icinga 2 instance.

SYNOPSIS
--------

```
icinga2-usersyncd [-h] [-V] [-v] [-q] [-c CONFIG] [--no-config]
                  [-L URL] [-u USERNAME] [-p PASSWORD] [-C CERT]
                  [-K KEY] [-A CA_CERT] [-Q QUEUE] [-P PREFIX]
                  [-T TEMPLATES] [-f FILTER] [-t DELAY]
```

DESCRIPTION
-----------

`icinga2-usersyncd` is a daemon to synchronize ApiUser  entries  with
Host agents on an Icinga 2 instance.

Options:

  * `-h`, `--help` show this help message and exit;

  * `-V`, `--version` show program's version information and exit;

  * `-v`, `--verbose` show more messages;

  * `-q`, `--quiet` show less messages;

  * `-c CONFIG`, `--config CONFIG` configuration file (the default is
    `/etc/sysconfig/icinga2-usersyncd`);

  * `--no-config` do not use a configuration file;

  * `-L URL`, `--url URL` Icinga 2 API URL;

  * `-u USERNAME`, `--username USERNAME` username to authenticate to
    Icinga 2 API;

  * `-p PASSWORD`, `--password PASSWORD` password to authenticate
    to Icinga 2 API;

  * `-C CERT`, `--cert CERT` certificate to authenticate to
    Icinga 2 API;

  * `-K KEY`, `--key KEY` key to authenticate to Icinga 2 API;

  * `-A CA_CERT`, `--ca CA_CERT` Icinga 2 API certificate (CA);

  * `-Q QUEUE`, `--queue QUEUE` event queue name to use (the default
    is either from the config or 'icinga2-usersyncd' if omitted);

* `-P PREFIX`, `--prefix PREFIX` a  prefix  for ApiUser names
    (the default is either from the config or 'host-' if omitted);

* `-T TEMPLATES`, `--templates TEMPLATES` a set of templates each
    created ApiUser should import (the default is either from the
    config or [usersync] if omitted);

* `-f FILTER`, --filter FILTER` an optional Host filter string;

* `-t DELAY`, `--delay DELAY` a number of seconds to wait between
    connection attempts (the default is either from the config or 1
    if omitted).

BUGS
----

Report bugs to https://bugzilla.altlinux.org/.

SEE ALSO
--------

`icinga2(8)`
