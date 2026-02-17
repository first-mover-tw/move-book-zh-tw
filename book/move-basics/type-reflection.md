---

description: "Type reflection in Move: inspect type names at runtime using std::type_name for dynamic type checks in smart contracts."
---

# 類型反射 (Type Reflection)

在程式語言中，_反射 (Reflection)_ 是指程式檢查並修改自身結構和行為的能力。Move 支援有限形式的反射，讓您可以在執行時期檢查值的類型。當您需要在同質集合 (homogeneous collection) 中儲存類型資訊，或者想檢查某個類型是否來自特定的套件時，這非常有用。

類型反射實作在 [標準庫](./standard-library) 模組 [`std::type_name`][type-name-stdlib] 中。它提供了一組函式，其中最主要的是 `with_defining_ids` 和 `with_original_ids`。

```move
let defining_type_name: TypeName = type_name::with_defining_ids<T>();
let original_type_name: TypeName = type_name::with_original_ids<T>();

// 僅返回套件的 "ID"。
let defining_package: address = type_name::defining_id<T>();
let original_package: address = type_name::original_id<T>();
```

## 定義 ID (Defining IDs) vs. 原始 ID (Original IDs)

瞭解 _定義 ID_ 和 _原始 ID_ 之間的區別非常重要。

- **原始 ID** 是套件第一次發佈時的 ID（在第一次升級之前）。
- **定義 ID** 是引入該反射類型的套件 ID，當在套件升級中引入新類型時，此屬性變得至關重要。

例如，假設一個套件的第一個版本發佈在 `0xA` 並引入了 `Version1` 類型。隨後，在一次升級中，該套件移動到了地址 `0xB` 並引入了一個新類型 `Version2`。對於 `Version1`，定義 ID 和原始 ID 是相同的。然而，對於 `Version2`，它們則不同：原始 ID 是 `0xA`，而定義 ID 是 `0xB`。

```move
// 注意：值 `0xA` 和 `0xB` 僅用於說明目的！
// 請勿嘗試執行此程式碼，因為它必然會失敗。
module book::upgrade;

// 在初始版本中引入。
// 定義 ID：0xA
// 原始 ID：0xA
//
// 使用定義 ID：0xA::upgrade::Version1
// 使用原始 ID：0xA::upgrade::Version1
public struct Version1 has drop {}

// 在套件升級中引入。
// 定義 ID：0xB
// highlight-important
// 原始 ID：0xA
//
// 使用定義 ID：0xB::upgrade::Version2
// highlight-important
// 使用原始 ID：0xA::upgrade::Version2
public struct Version2 has drop {}
```

## 實務應用

這個模組非常直觀，對結果允許的操作僅限於獲取字串表示形式，以及提取該類期的模組和地址。

```move file=packages/samples/sources/move-basics/type-reflection.move anchor=main

```

## 延伸閱讀

- [`std::type_name`][type-name-stdlib] 模組文件。

[type-name-stdlib]: https://docs.sui.io/references/framework/std/type_name
