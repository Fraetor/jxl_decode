# jxl_decode

A pure python JPEG XL decoder. It is currently *very* incomplete.

## Installation

I am aiming to make this decoder as portable as possible. As such it will
ideally have minimal dependencies outside of the standard library. I may use a
dependency for PNG output, if I don't write one myself.

### Requirements

- Recent [Python 3](https://www.python.org/) (developed with 3.11, but may work with some older versions)

### Development Requirements

- [PyTest](https://docs.pytest.org/)

## Usage

We are a long way away from it, but this is how I intend the decoder to work
from the command line:

```sh
jxl_decode input_file.jxl [output_file.png]
```

## Roadmap/To Do

- [ ] Add tests (and possibly some more useful methods) to Bitstream class.
- [ ] Decide on internal representation of image data (NumPy array?)
- [x] Define external interfaces by decoding PPM image.
- [ ] PNG output of decoded images.
- [ ] Decode JPEG images.
- [ ] Start on JPEG XL support.

<!-- ## Contributing

State if you are open to contributions and what your requirements are for
accepting them.

For people who want to make changes to your project, it's helpful to have some
documentation on how to get started. Perhaps there is a script that they should
run or some environment variables that they need to set. Make these steps
explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help
to ensure high code quality and reduce the likelihood that the changes
inadvertently break something. Having instructions for running tests is
especially helpful if it requires external setup, such as starting a Selenium
server for testing in a browser. -->

<!-- ## Acknowledgements

Show your appreciation to those who have contributed to the project. -->

## Licence

This software is available under the [MIT Licence](LICENCE.md).
