---
description: 型別反射 (Type Reflection) — 使用 `std::type_name` 在執行期檢查型別名稱，供智能合約進行動態型別檢查
---

# 型別反射 (Type Reflection) {#type-reflection}

在程式語言中，_反射_（reflection）是程式檢視並修改自身結構與行為的能力。Move 支援有限形式的反射，讓你可以在執行期檢查一個值的型別。這在你需要把型別資訊存進同質集合，或想檢查某型別是否來自特定套件時很方便。

型別反射是在 [標準函式庫](./standard-library) 模組 [`std::type_name`][type-name-stdlib] 中實作的。其主要函式為 `with_defining_ids` 與 `with_original_ids`，它們會把型別擷取為 `TypeName` 值；還有較輕量的對應版本，只回傳套件位址：

```move
let defining_type_name: TypeName = type_name::with_defining_ids<T>();
let original_type_name: TypeName = type_name::with_original_ids<T>();

// 只回傳套件的 "ID"。
let defining_package: address = type_name::defining_id<T>();
let original_package: address = type_name::original_id<T>();
```

## 定義 ID 與原始 ID (Defining IDs vs. Original IDs) {#defining-ids-vs-original-ids}

理解 _defining ID_ 與 _original ID_ 之間的差異很重要。

- Original ID 是套件第一次發布時的 ID（即第一次升級之前）。
- Defining ID 是引入該反射型別的套件 ID，這個屬性在套件升級中引入新型別時變得至關重要。

舉例來說，假設某套件第一版發布在 `0xA`，並引入了型別 `Version1`。之後在一次升級中，該套件移到位址 `0xB`，並引入了新型別 `Version2`。對於 `Version1`，defining ID 與 original ID 相同。然而對於 `Version2`，兩者不同：original ID 是 `0xA`，而 defining ID 是 `0xB`。

```move
// 注意：0xA 與 0xB 這兩個值僅供示範用途！
// 請勿嘗試執行此程式碼，因為它必然會失敗。
module book::upgrade;

// 於初始版本引入。
// Defining ID: 0xA
// Original ID: 0xA
//
// With Defining IDs: 0xA::upgrade::Version1
// With Original IDs: 0xA::upgrade::Version1
public struct Version1 has drop {}

// 於套件升級中引入。
// Defining ID: 0xB
// highlight-important
// Original ID: 0xA
//
// With Defining IDs: 0xB::upgrade::Version2
// highlight-important
// With Original IDs: 0xA::upgrade::Version2
public struct Version2 has drop {}
```

## 實務應用 (In Practice) {#in-practice}

這個模組很直觀：對產出的 `TypeName` 所允許的操作，僅限於取得字串表示，以及擷取該型別的模組名稱與位址。

```move file=packages/samples/sources/move-basics/type-reflection.move anchor=main

```

## 延伸閱讀 (Further Reading) {#further-reading}

- [std::type_name][type-name-stdlib] 模組文件。

[type-name-stdlib]: https://docs.sui.io/references/framework/std/type_name
