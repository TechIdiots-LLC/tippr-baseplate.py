# baseplate.py (tippr's fork)

This is [tippr](https://github.com/TechIdiots-LLC/tippr)'s maintained fork of
reddit's [baseplate.py](https://github.com/reddit/baseplate.py). reddit
archived the original in 2025; tippr's web app and its services
([activity](https://github.com/TechIdiots-LLC/tippr-service-activity),
[websockets](https://github.com/TechIdiots-LLC/tippr-service-websockets))
still use it, so it's kept working here on current Python and packages.

What's different from reddit's last release (2.7.2b4):

* No `pkg_resources`: the version is read with `importlib.metadata`, so it
  works with current setuptools.
* OpenTelemetry 1.28.2 / 0.49b2 (releases that don't need `pkg_resources`).
* Sentry setup that works with newer sentry-sdk versions.

Work happens on `develop`. tippr pins a commit of it in its
`install/requirements.txt`:

```
baseplate @ git+https://github.com/TechIdiots-LLC/tippr-baseplate.py@<commit>
```

Issues and pull requests are welcome here. reddit's
[documentation](https://baseplate.readthedocs.io/en/stable/) still describes
the library, and its [contribution guidelines](CONTRIBUTING.md) still apply.

## What baseplate is

It's much easier to manage a bunch of services when they all have the same
shape: the way they're developed, the way they interact with the infrastructure
they run on, and the way they interact with each other. Baseplate is reddit's
specification for the common shape of their services. This library,
Baseplate.py, is the Python implementation of that specification.

Baseplate.py glues together tooling for interacting with a service backend
and spackles over things that are missing. It integrates with Apache
Thrift, Pyramid, and client libraries for many systems to transparently make
your applications observable.

Baseplate applications transparently get:

* Timing and request rate metrics using statsd
* Distributed tracing
* Error reporting and aggregation with Sentry

And can take advantage of:

* Integration with commonly used clients like: Thrift, SQLAlchemy,
  cassandra-driver, pymemcache, redis-py, and Kombu
* Secrets securely pulled from Vault

And many other things!

## pre-commit

* [Documentation](https://pre-commit.com/)

This repo comes with pre-commit hooks that let you (on a voluntary basis)
enable pre-commit and/or pre-push hooks.

Configuration can be found at the root of the directory in
`.pre-commit-config.yaml`. On its own, the configuration file doesn't do
anything. You either need to [run the hooks manually](https://pre-commit.com/#pre-commit-run)
or [install them](https://pre-commit.com/#pre-commit-install) so that they run
automatically on every commit or push.

Currently, we run the `make fmt` target on commit and `make lint` / `pytest`
actions on push.

Specific hooks can be [temporarily disabled](https://pre-commit.com/#temporarily-disabling-hooks).

You can install hooks only for a specific step (i.e. [pre-push](https://pre-commit.com/#pre-commit-during-push)).

## Testing a change in tippr

Point tippr's `install/requirements.txt` at your branch or commit and
reinstall:

```
baseplate @ git+https://github.com/TechIdiots-LLC/tippr-baseplate.py@<ref>
```

A tippr release should pin a commit, not a branch.

## License and credit

BSD 3-clause ([LICENSE](LICENSE)). Original code © reddit Inc.; changes since
the fork by TechIdiots LLC.
