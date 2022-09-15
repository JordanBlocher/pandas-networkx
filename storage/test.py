import warnings


def run(verbosity=1):
    warnings.warn(
        (
            "`run` is deprecated and will be removed in version 3.0.\n"
            "Call `pytest` directly from the commandline instead.\n"
        ),
        DeprecationWarning,
    )

    import pytest

    pytest_args = ["-l"]

    if verbosity and int(verbosity) > 1:
        pytest_args += ["-" + "v" * (int(verbosity) - 1)]

    pytest_args += ["--pyargs", "auction"]

    try:
        code = pytest.main(pytest_args)
    except SystemExit as err:
        code = err.code

    return code == 0


if __name__ == "__main__":
    run()
