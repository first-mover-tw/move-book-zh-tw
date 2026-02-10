# 模組 (Module)

<!--

Chapter: Base Syntax
Goal: Introduce module keyword.
Notes:
    - modules are the base unit of code organization
    - module members are private by default
    - types internal to the module have special access rules
    - only module can pack and unpack its types

 -->

模組是 Move 中程式碼組織的基本單位。模組用於分組和隔離程式碼，預設情況下，模組的所有成員對該模組而言都是私有的。在本節中，您將學習如何定義模組、宣告其成員，以及如何從其他模組存取它。

## 模組宣告

使用 `module` 關鍵字後接套件地址、模組名稱、分號及模組主體來宣告模組。模組名稱應使用 **蛇形命名法 (snake_case)** — 即全小寫字母，單字之間以底線分隔。在一個套件中，模組名稱必須是唯一的。

通常，`sources/` 資料夾中的一個檔案包含一個模組。檔案名稱應與模組名稱相匹配 — 例如，`donut_shop` 模組應儲存在 `donut_shop.move` 檔案中。您可以在 [編碼規範](./../guides/code-quality-checklist) 節點中閱讀更多相關資訊。

> 如果您需要在一個檔案中宣告多個模組，則必須使用 [模組區塊 (Module Block)](#module-block) 語法。

```move file=packages/samples/sources/move-basics/module-label.move anchor=module

```

結構、函式、常數和匯入都是模組的一部份：

- [結構 (Structs)](./struct)
- [函式 (Functions)](./function)
- [常數 (Constants)](./constants)
- [匯入 (Imports)](./importing-modules)
- [結構方法 (Struct Methods)](./struct-methods)

## 地址與具名地址 (Address and Named Address)

模組地址可以透過以下兩種方式指定：位址 **常數 (literal)**（不需要 `@` 前綴）或在 [套件清單 (Package Manifest)](./../concepts/manifest) 中指定的 **具名地址**。在下面的範例中，兩者是相同的，因為 `Move.toml` 的 `[addresses]` 部分中有一條 `book = "0x0"` 的紀錄。

```move file=packages/samples/sources/move-basics/module.move anchor=address_literal

```

Move.toml 中的地址部分：

```toml
# Move.toml
[addresses]
book = "0x0"
```

## 模組成員

模組成員在模組主體內宣告。為了說明這一點，讓我們定義一個包含結構、函式和常數的簡單模組：

```move file=packages/samples/sources/move-basics/module-members.move anchor=members

```

## 模組區塊 (Module Block)

2024 版本之前的 Move 要求模組的主體必須是一個 **模組區塊** — 即模組的內容需要被大括號 `{}` 包圍。使用區塊語法（而非 **標籤 (label)** 語法）的主要原因是如果您需要在一個檔案中定義多個模組。然而，不建議在實務中使用模組區塊。

```move file=packages/samples/sources/move-basics/module.move anchor=members

```

## 延伸閱讀

- Move 參考手冊中的 [模組 (Modules)](./../../reference/modules)。
