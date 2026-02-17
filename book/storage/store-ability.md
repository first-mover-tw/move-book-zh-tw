---

description: "The store ability in Move allows types to be used as fields in objects and enables public transfer and storage operations on Sui."
---

# 能力：Store (Ability: Store)

[`key` 能力][key-ability] 要求所有欄位都具有 `store`，這就定義了 `store` 能力的含義：它是作為物件欄位的能力。具有 [`copy`][copy-ability] 或 [`drop`][drop-ability] 但沒有 `store` 的結構永遠不能被「存儲」。具有 `key` 但沒有 `store` 的類型不能被包裝 (wrapped) —— 即作為另一個物件的欄位使用，且受限於始終保持在頂層。

## 定義

`store` 能力允許類型的實體作為具有 `key` 能力結構中的一個欄位。

```move
// hidden-block-start
use std::string::String;

// hidden-block-end
/// 帶有 `store` 的額外後設資料；所有欄位也必須具有 `store`！
public struct Metadata has store {
    bio: String,
}

/// 單個使用者記錄的物件。
public struct User has key {
    id: UID,
    name: String,       // String 具有 `store`
    age: u8,            // 所有整數都具有 `store`
    metadata: Metadata, // 另一個具有 `store` 能力的類型
}
```

## 與 `copy` 和 `drop` 的關係

所有三種非 `key` 能力都可以以任何組合使用。

## 與 `key` 的關係

具有 `store` 能力的物件可以「存儲」在其他物件中。

> 雖然不是語言或校驗器功能，但 `store` 充當結構上的一個「公開 (public)」修飾符，允許呼叫那些沒有 [內部約束 (internal constraint)](./internal-constraint.md) 的公開 [轉移函式 (transfer functions)](./storage-functions.md)。

## 具有 `store` 能力的類型

Move 中除參考之外的所有原生類型都具有 `store` 能力。這包括：

- [布林值 (bool)](./../move-basics/primitive-types.md#booleans)
- [無符號整數 (unsigned integers)](./../move-basics/primitive-types.md#integer-types)
- [向量 (vector)](./../move-basics/vector.md)
- [地址 (address)](./../move-basics/address.md)

標準函式庫中定義的所有類型也具有 `store` 能力。這包括：

- [選項 (Option)](./../move-basics/option.md)
- [字串 (String)](./../move-basics/string.md) 和 [ASCII 字串 (ASCII String)](./../move-basics/string.md)
- [類型名稱 (TypeName)](./../move-basics/type-reflection.md)

## 延伸閱讀

- Move 參考手冊中的 [類型能力 (Type Abilities)](./../../reference/abilities)。

[key-ability]: ./key-ability.md
[drop-ability]: ./../move-basics/drop-ability.md
[copy-ability]: ./../move-basics/copy-ability.md
