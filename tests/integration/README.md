# Integration & Performance Tests

These tests use [VCR.py](https://vcrpy.readthedocs.io/) cassettes to avoid making real HTTP requests. Due to the size of the cassettes, they are not included in this repository. 

## Downloading Cassettes

Cassettes are distributed from releases in a [separate repository](https://github.com/GateNLP/usp-test-cassettes). For an overview of available cassettes, see [the manifest file](https://github.com/GateNLP/usp-test-cassettes/blob/main/manifest.json).

Run `python3 download.py` to download and decompress all available cassettes into the `cassettes` directory.

Some cassette files are quite large when decompressed (~400MB) but compress relatively efficiently (~30MB).

> [!IMPORTANT]  
> In USP's tests, VCR.py is configured to run in `none` record mode (HTTP requests not included in the cassette will cause failure).
> This means that code changes causing new HTTP requests will temporarily break performance tests until the cassettes can be updated.

## Running Tests

Integration tests must be manually enabled with the `--integration` flag. 

```bash
pytest --integration tests/integration
```

## Memory Profiling with Memray

To profile memory usage during tests, run the test command with the `--memray`

```bash
pytest --memray [--memray-bin-path memray] --integration tests/integration
```

Without the --memray-bin-path argument, this will measure memory usage and report at the end of the test run.
With the argument, it will output the memory usage reports to the `memray` directory, which can then be used to generate reports e.g. [a flamegraph](https://bloomberg.github.io/memray/flamegraph.html).


## Performance Profiling with Pyinstrument

To profile performance during tests, run through the pyinstrument CLI:

```bash
pyinstrument -m pytest --integration tests/integration
```

Pyinstrument does not distinguish between tests, so you may want to filter to a specific test at a time with -k. For example, to only run the bbc.co.uk test:

```bash
pyinstrument -m pytest --integration -k bbc tests/integration
```

This can be viewed as an interactive HTML report by passing `-r html` to `pyinstrument` initially, or using the `--load-prev` command output at the end of the test run.