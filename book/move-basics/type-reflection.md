---
description: Move 中的型別反射 (type reflection)：在執行階段使用 `std::type_name` 檢查型別名稱，以便在智慧合約 (smart contracts) 中進行動態型別檢查。
title: 型別反射 (Type Reflection)
keywords:
  - Move
  - Sui
  - Move tutorial
  - type
  - reflection
  - type system
questions:
  - What is Type Reflection in Move?
  - How do I use Type Reflection in Move?
  - What is Defining IDs vs. Original IDs in Move?
  - What is In Practice in Move?
answer: 'Type reflection in Move: inspect type names at runtime using std::type_name for dynamic type checks in smart contracts.'
goal:
  description: 'Reader understands type reflection in Move: inspect type names at runtime using std::type_name for dynamic type checks in smart contracts'
  requires:
    - has_frontmatter:
        - title
        - description
        - keywords
      label: Has required frontmatter fields
    - min_words: 50
      label: Needs content depth
    - has_questions: true
      label: Needs questions for AI search visibility
    - has_answer: true
      label: Needs answer summary for AI citation
---

# 型別反射 (Type Reflection) {#type-reflection}

在程式語言中，_reflection_（反射）是指程式能夠檢視並修改其自身結構與行為的能力。Move 支援一種受限形式的反射，讓你可以在執行階段檢查值的型別。當你需要在同質集合中儲存型別資訊，或想檢查某個型別是否來自特定套件時，這項功能十分實用。

型別反射實作於 [Standard Library](./standard-library) 模組
[`std::type_name`][type-name-stdlib] 中。其主要函式為 `with_defining_ids` 與
`with_original_ids`，會將型別擷取為 `TypeName` 值；另外也有較精簡的對應函式，
僅回傳套件地址：

```move
let defining_type_name: TypeName = type_name::with_defining_ids<T>();
let original_type_name: TypeName = type_name::with_original_ids<T>();

// 僅回傳套件的「ID」。
let defining_package: address = type_name::defining_id<T>();
let original_package: address = type_name::original_id<T>();
```

## 定義 ID 與原始 ID (Defining IDs vs. Original IDs) {#defining-ids-vs-original-ids}

了解 _defining ID_（定義 ID）與 _original ID_（原始 ID）之間的差異十分重要。

- 原始 ID 是套件第一次發佈時的 ID（首次升級之前）。
- 定義 ID 是引入被反射型別的套件 ID；當套件升級時引入新型別，這項屬性便十分關鍵。

例如，假設某套件的第一個版本發佈於 `0xA`，並引入型別
`Version1`。之後在升級時，套件移至地址 `0xB`，並引入新的型別
`Version2`。對於 `Version1`，定義 ID 與原始 ID 相同。然而對於 `Version2`，
兩者不同：原始 ID 是 `0xA`，而定義 ID 是 `0xB`。

```move
// 注意：值 `0xA` 與 `0xB` 僅用於說明用途！
// 請勿嘗試執行此程式碼，因為它必定會失敗。
module book::upgrade;

// 於初始版本中引入。
// 定義 ID：0xA
// 原始 ID：0xA
//
// 使用定義 ID：0xA::upgrade::Version1
// 使用原始 ID：0xA::upgrade::Version1
public struct Version1 has drop {}

// 於套件升級時引入。
// 定義 ID：0xB
// 突顯-重要
// 原始 ID：0xA
//
// 使用定義 ID：0xB::upgrade::Version2
// 突顯-重要
// 使用原始 ID：0xA::upgrade::Version2
public struct Version2 has drop {}
```

## 實務應用 (In Practice) {#in-practice}

此模組相當直觀：對產生的 `TypeName` 可進行的操作，僅限於取得字串表示形式，以及擷取型別的模組名稱與地址。

```move file=packages/samples/sources/move-basics/type-reflection.move anchor=main

```

## 延伸閱讀 (Further Reading) {#further-reading}

- [std::type_name][type-name-stdlib] 模組文件。

[type-name-stdlib]: https://docs.sui.io/references/framework/std/type_name
