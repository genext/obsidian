---
title: "pdf"
created: 2023-09-12 10:13:03
updated: 2025-09-29 09:54:19
---
  * pdf 저장 형식
    * "dict" in PDF #memo ^Eqgp177uY
      * A dictionary object is a fundamental PDF data type that stores key-value pairs.

Key Points:
  Syntax: Enclosed in << key value >> brackets
  Keys: Name objects starting with / (e.g., /Type, /MediaBox)
  Values: Any PDF object type (numbers, strings, arrays, other dictionaries)

Common Uses:
  Page objects (define page properties)
  Font dictionaries (font characteristics)
  Image dictionaries (image data/properties)
  Catalog dictionary (document root structure)
  Annotation dictionaries (interactive elements)

Example
```plain text
<< /Type /Page
  /MediaBox [0 0 612 792]
  /Resources << /Font << /F1 5 0 R >> >>
>>

Same example in JSON format
{
  "Type": "Page",
  "MediaBox": [0, 0, 612, 792],
  "Resources": {
    "Font": {
      "F1": "5 0 R"
    }
  }
}
```