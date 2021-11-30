# xarray-dataclasses

[![PyPI](https://img.shields.io/pypi/v/xarray-dataclasses.svg?label=PyPI&style=flat-square)](https://pypi.org/project/xarray-dataclasses/)
[![Python](https://img.shields.io/pypi/pyversions/xarray-dataclasses.svg?label=Python&color=yellow&style=flat-square)](https://pypi.org/project/xarray-dataclasses/)
[![Test](https://img.shields.io/github/workflow/status/astropenguin/xarray-dataclasses/Test?logo=github&label=Test&style=flat-square)](https://github.com/astropenguin/xarray-dataclasses/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?label=License&style=flat-square)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.4624819-blue?style=flat-square)](https://doi.org/10.5281/zenodo.4624819)

xarray extension for typed DataArray and Dataset creation


## Overview

xarray-dataclasses is a Python package that makes it easy to create typed DataArray and Dataset objects of [xarray] using [the Python's dataclass].

```python
from dataclasses import dataclass
from typing import Literal
from xarray_dataclasses import AsDataArray, Coord, Data


X = Literal["x"]
Y = Literal["y"]


@dataclass
class Image(AsDataArray):
    """Specs for a monochromatic image."""

    data: Data[tuple[X, Y], float]
    x: Coord[X, int] = 0
    y: Coord[Y, int] = 0


# create an image as DataArray
image = Image.new([[0, 1], [2, 3]], x=[0, 1], y=[0, 1])

# create an image filled with ones
ones = Image.ones((2, 2), x=[0, 1], y=[0, 1])
```

### Features

- DataArray and Dataset objects with fixed dimensions, data type, and coordinates can easily be created.
- NumPy-like special functions such as ``ones()`` are provided as class methods.
- Compatible with [the Python's dataclass].
- Compatible with static type check by [Pyright].

### Installation

```shell
$ pip install xarray-dataclasses
```


## Background

[xarray] is useful for handling labeled multi-dimensional data, but it is a bit troublesome to create DataArray and Dataset objects with fixed dimensions, data type, or coordinates (typed DataArray and typed Dataset).
For example, let us think about the following DataArray specifications for a monochromatic image.

- Dimensions of data must be `("x", "y")`.
- Data type of data must be `float`.
- Data type of dimensions must be `int`.
- Default value of dimensions must be `0`.

Then a function to create a typed DataArray object is something like this.

```python
import numpy as np
import xarray as xr


def create_image(data, x=0, y=0):
    """Create a monochromatic image."""
    data = np.array(data)

    if x == 0:
        x = np.full(data.shape[0], x)
    else:
        x = np.array(x)

    if y == 0:
        y = np.full(data.shape[1], y)
    else:
        y = np.array(y)

    return xr.DataArray(
        data=data.astype(float),
        dims=("x", "y"),
        coords={
            "x": ("x", x.astype(int)),
            "y": ("y", y.astype(int)),
        },
    )


image = create_image([[0, 1], [2, 3]])
```

The issues are

- It is not easy to figure out the specifications from the code.
- It is not easy to reuse the code, for example, to add new coordinates.

xarray-dataclasses resolves them by defining the specifications as a dataclass.
As shown in the code in the overview, the specifications become much easier to read.

- The type hints have complete information for DataArray creation.
- The default values are given as class variables.
- The mix-in class `AsDataArray` provides class methods such as `new()`.
- The extension of the specifications is easy by class inheritance.

## Basic usage

xarray-dataclasses uses [the Python's dataclass].
Please learn how to use it before proceeding.
Data (or data variables), coordinates, attributes, and a name of a DataArray or a Dataset object are defined as dataclass fields with the following type hints.
Note that the following code is supposed in the examples below.

```python
from dataclasses import dataclass
from typing import Literal
from xarray_dataclasses import AsDataArray, AsDataset
from xarray_dataclasses import Attr, Coord, Data, Name


X = Literal["x"]
Y = Literal["y"]
```

### Data field

The data field is a field whose value will become the data of a DataArray object or a data variable of a Dataset object.
The type hint `Data[TDims, TDtype]` fixes the dimensions and the data type of the object.
Here are some examples of how to specify them.

Type hint | Inferred dimensions
--- | ---
`Data[Literal[()], ...]` | `()`
`Data[Literal["x"], ...]` | `("x",)`
`Data[tuple[Literal["x"], Literal["y"]], ...]` | `("x", "y")`

Type hint | Inferred data type
--- | ---
`Data[..., Any]` | `None`
`Data[..., None]` | `None`
`Data[..., float]` | `numpy.dtype("float64")`
`Data[..., numpy.float128]` | `numpy.dtype("float128")`
| `Data[..., Literal["datetime64[ns]"]]` | `numpy.dtype("<M8[ns]")`

### Coordinate field

The coordinate field is a field whose value will become a coordinate of a DataArray or a Dataset object.
The type hint `Coord[TDims, TDtype]` fixes the dimensions and the data type of the object.

### Attribute field

The attribute field is a field whose value will become an attribute of a DataArray or a Dataset object.
The type hint `Attr[T]` specifies the type of the value, which is used only for static type check.

### Name field

The name field is a field whose value will become the name of a DataArray object.
The type hint `Name[T]` specifies the type of the value, which is used only for static type check.

### DataArray class

The DataArray class is a dataclass that defines typed DataArray specifications.
Exactly one data field is allowed in a DataArray class.
The second and subsequent data fields are just ignored in DataArray creation.

```python
@dataclass
class Image(AsDataArray):
    """Specs for a monochromatic image."""

    data: Data[tuple[X, Y], float]
    x: Coord[X, int] = 0
    y: Coord[Y, int] = 0
    units: Attr[str] = "cd / m^2"
    name: Name[str] = "luminance"
```

A DataArray object is created by the shorthand method `new()`.

```python
Image.new([[0, 1], [2, 3]], x=[0, 1], y=[0, 1])

<xarray.DataArray "luminance" (x: 2, y: 2)>
array([[0., 1.],
       [2., 3.]])
Coordinates:
  * x        (x) int64 0 1
  * y        (y) int64 0 1
Attributes:
    units:    cd / m^2
```

NumPy-like `empty()`, `zeros()`, `ones()`, `full()` methods are available.

```python
Image.ones((3, 3))

<xarray.DataArray "luminance" (x: 3, y: 3)>
array([[1., 1., 1.],
       [1., 1., 1.],
       [1., 1., 1.]])
Coordinates:
  * x        (x) int64 0 0 0
  * y        (y) int64 0 0 0
Attributes:
    units:    cd / m^2
```

### Dataset class

The Dataset class is a dataclass that defines typed Dataset specifications.
Multiple data fields are allowed to define the data variables of the object.

```python
@dataclass
class ColorImage(AsDataset):
    """Specs for a color image."""

    red: Data[tuple[X, Y], float]
    green: Data[tuple[X, Y], float]
    blue: Data[tuple[X, Y], float]
    x: Coord[X, int] = 0
    y: Coord[Y, int] = 0
    units: Attr[str] = "cd / m^2"
```

A Dataset object is created by the shorthand method `new()`.

```python
ColorImage.new(
    [[0, 0], [0, 0]],  # red
    [[1, 1], [1, 1]],  # green
    [[2, 2], [2, 2]],  # blue
)

<xarray.Dataset>
Dimensions:  (x: 2, y: 2)
Coordinates:
  * x        (x) int64 0 0
  * y        (y) int64 0 0
Data variables:
    red      (x, y) float64 0.0 0.0 0.0 0.0
    green    (x, y) float64 1.0 1.0 1.0 1.0
    blue     (x, y) float64 2.0 2.0 2.0 2.0
Attributes:
    units:    cd / m^2
```

## Advanced usage

### Coordof and Dataof type hints

xarray-dataclasses provides advanced type hints, `Coordof[T]` and `Dataof[T]`.
Unlike `Data` and `Coord`, they specify a dataclass that defines a DataArray class.
This is useful, for example, when users want to add metadata to dimensions for [plotting].

```python
from xarray_dataclasses import Coordof


@dataclass
class XAxis:
    """Specs for the x axis."""

    data: Data[X, int]
    long_name: Attr[str] = "x axis"
    units: Attr[str] = "pixel"


@dataclass
class YAxis:
    """Specs for the y axis."""

    data: Data[Y, int]
    long_name: Attr[str] = "y axis"
    units: Attr[str] = "pixel"


@dataclass
class Image(AsDataArray):
    """Specs for a monochromatic image."""

    data: Data[tuple[X, Y], float]
    x: Coordof[XAxis] = 0
    y: Coordof[YAxis] = 0
```

### Options for DataArray and Dataset creation

For customization, users can add a special class attribute, `__dataoptions__`, to a DataArray or Dataset class.
A custom factory for DataArray or Dataset creation is only supported in the current implementation.


```python
import xarray as xr
from xarray_dataclasses import DataOptions


class Custom(xr.DataArray):
    """Custom DataArray."""

    __slots__ = ()

    def custom_method(self) -> None:
        print("Custom method!")


dataoptions = DataOptions(Custom)


@dataclass
class Image(AsDataArray):
    """Specs for a monochromatic image."""

    __dataoptions__ = dataoptions

    data: Data[tuple[X, Y], float]
    x: Coord[X, int] = 0
    y: Coord[Y, int] = 0


image = Image.ones([3, 3])
isinstance(image, Custom)  # True
image.custom_method()  # Custom method!
```

### DataArray and Dataset creation without shorthands

xarray-dataclasses provides functions, `asdataarray` and `asdataset`.
This is useful, for example, users do not want to inherit the mix-in class (`AsDataArray` or `AsDataset`) in a DataArray or Dataset dataclass.

```python
from xarray_dataclasses import asdataarray


@dataclass
class Image:
    """Specifications of images."""

    data: Data[tuple[X, Y], float]
    x: Coord[X, int] = 0
    y: Coord[Y, int] = 0


image = asdataarray(Image([[0, 1], [2, 3]], x=[0, 1], y=[0, 1]))
```


<!-- References -->
[Pyright]: https://github.com/microsoft/pyright
[the Python's dataclass]: https://docs.python.org/3/library/dataclasses.html
[xarray]: https://xarray.pydata.org/en/stable/index.html
[plotting]: https://xarray.pydata.org/en/stable/user-guide/plotting.html#simple-example
