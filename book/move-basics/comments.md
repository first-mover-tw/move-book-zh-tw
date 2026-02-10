# 註解 (Comments)

<!--

Chapter: Basic Syntax
Goal: Introduce comments.
Notes:
    - doc comments are used in docgen
    - only public members are documented
    - doc comments are placed in between attributes and the definition
    - doc comments are allowed for: modules, structs, functions, constants
    - give an example of how doc comments are translated
 -->

註解是用於添加筆記或記錄程式碼的一種方式。它們會被編譯器忽略，不會產生 Move 位元組碼。您可以使用註解來解釋程式碼的功能、為自己或其他開發人員留註記、暫時移除部分程式碼或生成文檔。Move 中有三種類型的註解：行註解、區塊註解和文檔註解。

## 行註解 (Line Comment)

您可以使用雙斜線 `//` 來註解掉該行的其餘部分。編譯器將忽略 `//` 之後的所有內容。

```move file=packages/samples/sources/move-basics/comments-line.move anchor=main

```

## 區塊註解 (Block Comment)

區塊註解用於註解掉一段程式碼。它們以 `/*` 開頭並以 `*/` 結尾。編譯器將忽略 `/*` 和 `*/` 之間的所有內容。您可以在使用區塊註解來註解掉單行或多行內容，甚至可以用它們來註解掉行內的一部份。

```move file=packages/samples/sources/move-basics/comments-block.move anchor=main

```

這個範例有點極端，但它展示了所有可以使用區塊註解的方式。

## 文檔註解 (Doc Comment)

文檔註解是用於為您的程式碼生成文檔的特殊註解。它們與行註解類似，但以三個斜線 `///` 開頭，並放置在它們所說明的項目定義之前。

```move file=packages/samples/sources/move-basics/comments-doc.move anchor=main

```

## 空白 (Whitespace)

與某些語言不同，空白（空格、Tab 和換行）對程式的含義沒有影響。

<!-- TODO: docgen, which members are in the documentation -->
