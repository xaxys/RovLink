# Bubbler

English | [简体中文](README_cn.md)

Bubbler is a proto generator optimized for IoT devices. It compiles the `.bb` proto file and generates the output in the specified target language.

Bubbler's proto powerful, and can be non-byte-aligned, which is useful for IoT devices with limited resources. Explained below.

Also, You may need syntax highlighting for `.bb` files, see [bubbler-vscode](https://github.com/xaxys/bubbler-vscode), or install it from [VSCode Marketplace](https://marketplace.visualstudio.com/items?itemName=xaxys.Bubbler).

Warning: Bubbler is still in development and is not ready for production use.

## Installation

```sh
git clone https://github.com/xaxys/bubbler.git
cd bubbler
go build
```

## Usage

```sh
bubbler [options] <input file>
```

### Options

- `-t <target>`: Target language
- `-o <output>`: Output file

### Target Languages

Run `bubbler` to see the list of supported target languages.

### Examples

```sh
bubbler -t c -o gen.c example.bb
bubbler -t dump example.bb
```

## Protocol Syntax

Bubbler uses a concise syntax to define data structures and enumeration types.

### Import Statements

Use the `import` keyword to import other Bubbler protocol files. For example:

```python
import "control.bb";
import "a.bb";
```

### Enumeration Types

Use the `enum` keyword to define enumeration types. The definition of an enumeration type includes the enumeration name and enumeration values. For example:

```c
enum FrameType[1] {
    SENSOR_PRESS = 0x00,
    SENSOR_HUMID = 0x01,
    CURRENT_SERVO_A = 0xA0,
    CURRENT_SERVO_B = 0xA1,
};
```

In this example, `FrameType` is an enumeration type with four enumeration values: `SENSOR_PRESS`, `SENSOR_HUMID`, `CURRENT_SERVO_A`, and `CURRENT_SERVO_B`.

Enumeration values cannot be negative (tentatively), and if the value is not filled in, the default value of the enumeration value is the previous enumeration value plus 1.

The number in the square brackets after the enumeration type name indicates the width of the enumeration type, for example, `[1]` indicates 1 byte. You can also use the `#` symbol to represent bytes and bits, for example, `#1` represents 1 bit, `#2` represents 2 bits. You can also use them in combination, for example, `1#4` represents 1 byte 4 bits, that is, 12 bits.

### Data Structures

Use the `struct` keyword to define data structures. The definition of a data structure includes the structure name and a series of fields. For example:

```bubbler
struct Frame[20] {
    FrameType opcode;
    struct some_embed[1] {
        bool valid[#1];
        bool error[#1];
        uint8 source[#3];
        uint8 target[#3];
    };
    uint8<18> payload;
};
```

In this example, `Frame` is a data structure with three fields: `opcode`, `some_embed`, and `payload`. `opcode` is of type `FrameType`, `some_embed` is an anonymous embedded data structure, and `payload` is of type `uint8`.

### Field Types

The Bubbler protocol supports four types of fields: regular fields, anonymous embedded fields, constant fields, and empty fields.

- Regular fields: Consist of a type name, field name, and field width (optional).
- Anonymous embedded fields: An anonymous field, which can be a struct definition or a defined struct name, its internal subfields will be promoted and expanded into the parent structure.
- Constant fields: A field with a fixed value, its value is determined at the time of definition and cannot be modified. The field name is optional. If there is a field name, the corresponding field will be generated. When encoding, the value of the constant field will be ignored. When decoding, the value of the constant field will be checked. If it does not match, an error will be reported.
- Empty fields: A field without a name and type, only width, used for placeholders.

#### Regular Fields

Regular fields consist of a type name, field name, and field width. For example:

```bubbler
struct Frame {
    RovlinkFrameType opcode;
};
```

In this example, `opcode` is a regular field, its type is `RovlinkFrameType`.

The field width is optional. If the width is not filled in, the field width is the width of the type.

The field width can be less than the width of the type, for example:

```c
struct Frame[20] {
    int64 myInt48[6];
};
```

In this example, `myInt48` is a 6-byte field, its type is `int64`, but its width is 6 bytes, so it will only occupy 6 bytes of space when encoding.

However, for fields of `struct` type, the field width must be equal to the width of the type (tentatively)

### Anonymous Embedded Fields

Anonymous embedded fields are nameless data structures that can contain multiple subfields. For example:

```bubbler
struct Frame {
    int64 myInt48[6];
    struct some_embed[1] {
        bool valid[#1];
        bool error[#1];
        uint8 source[#3];
        uint8 target[#3];
    };
};
```

In this example, `some_embed` is an anonymous embedded field, it contains four subfields: `valid`, `error`, `source`, and `target`.

The subfields of the anonymous embedded field will be promoted and expanded into the parent structure. The generated structure is as follows:

```c
struct Frame {
    int64_t myInt48;
    bool valid;
    bool error;
    uint8_t source;
    uint8_t target;
};
```

Anonymous embedded fields can also be a defined data structure, for example:

```c
struct AnotherTest {
    int8<2> arr;
}

struct Frame {
    int64 myInt48[6];
    AnotherTest;
    uint8<18> payload;
};
```

In this way, the generated structure is as follows:

```c
struct Frame {
    int64_t myInt48;
    int8_t arr[2];
    uint8_t payload;
};
```

### Constant Fields

Constant fields are fields with a fixed value, its value is determined at the time of definition and cannot be modified. For example:

```bubbler
struct Frame {
    uint8 FRAME_HEADER = 0xAA;
};
```

In this example, `FRAME_HEADER` is a constant field with a value of `0xAA`.

The value of the constant field will be ignored during encoding and checked during decoding. If it does not match, an error will be reported.

### Empty Fields

Empty fields are fields without a name and type, they only have a width. Empty fields are often used for padding or aligning data structures. For example:

```bubbler
struct Frame {
    void [#2];
};
```

In this example, `void [#2]` is an empty field that occupies 2 bits of space.

### Field Options

Field options are used to specify additional attributes of a field. For example, you can use the `order` option to specify the byte order of an array:

```bubbler
struct AnotherTest {
    int8<2> arr [order = "big"];
}
```

In this example, the byte order of the `arr` field is set to big-endian.

### Custom getter/setter

You can define custom getter and setter methods for a field to perform specific operations when reading or writing field values. For example:

```bubbler
struct SensorTemperatureData {
    uint16 temperature[2] {
        get(float64): value / 10 - 40;
        set(float64): value == 0 ? 0 : (value + 40) * 10;
        set AnotherCustomSet(uint8): value == 0 ? 0 : (value + 40) * 10;
    };
}
```

In this example, the `temperature` field has a custom getter method and two custom setter methods.

The default getter returns a `float64` type and calculates the result based on `value / 10 - 40`. Here, `value` is filled with the field value and is of type `uint16`.

The default setter accepts a `float64` type parameter and calculates the result based on `value == 0 ? 0 : (value + 40) * 10` to set the field value. Here, `value` is filled with the parameter value and is of type `float64`.

The custom setter named `AnotherCustomSet` takes a `uint8` type parameter. It calculates the result based on `value == 0 ? 0 : (value + 40) * 10` to set the field value. Here, `value` is filled with the parameter value and is of type `uint8`.

## Contributing

Contributions to Bubbler are welcome.

## License

MIT License