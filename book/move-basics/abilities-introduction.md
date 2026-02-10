# 能力：簡介 (Abilities: Introduction)

Move 擁有獨特的類型系統，允許自定義 **類型能力 (type abilities)**。
[在上一節](./struct)中，我們介紹了 `struct` 的定義及如何使用它。
然而，`Artist` 和 `Record` 結構的實例必須被解構 (unpack) 才能編譯通過。這是沒有 **能力** 的結構的預設行為。

> 在本書中，您會看到名為 `Ability: <名稱>` 的章節，其中 `<名稱>` 是能力的名稱。這些章節將詳細介紹該能力及其運作方式，以及如何在 Move 中使用它。

## 什麼是能力？

能力是一種允許類型具有某些行為的方式。它們是結構宣告的一部分，定義了結構實例允許具備哪些行為。

## 能力語法 (Abilities Syntax)

在結構定義中使用 `has` 關鍵字後接能力清單來設置能力。多個能力之間以逗號分隔。Move 支援 4 種能力：`copy`、`drop`、`key` 和 `store`。每種能力都定義了結構實例的特定行為。

```move
/// 此結構具有 `copy` 和 `drop` 能力。
public struct VeryAble has copy, drop {
    // field: Type1,
    // field2: Type2,
    // ...
}
```

## 概覽

各能力快速概覽：

> 除了 [參照 (references)](references) 之外，所有內建類型都具有 `copy`、`drop` 和 `store` 能力。參照則具有 `copy` 和 `drop`。

- `copy` — 允許結構被 **複製 (copied)**。在 [能力：複製 (Ability: Copy)](./copy-ability) 章節中詳細說明。
- `drop` — 允許結構被 **丟棄 (dropped)** 或捨棄。在 [能力：丟棄 (Ability: Drop)](./drop-ability) 章節中詳細說明。
- `key` — 允許結構在儲存空間中被用作 **鍵 (key)**。在 [能力：鍵 (Ability: Key)](./../storage/key-ability) 章節中詳細說明。
- `store` — 允許結構被 **儲存 (stored)** 在具有 _key_ 能力的結構中。在 [能力：儲存 (Ability: Store)](./../storage/store-ability) 章節中詳細說明。

雖然在此僅做簡要提及，但在後續章節中我們將深入探討每種能力，並提供如何使用它們的具體背景資訊。

## 無能力 (No Abilities)

沒有能力的結構既不能被捨棄、複製，也不能儲存在儲存空間中。我們將這種結構稱為 **燙手山芋 (Hot Potato)**。這是一個輕鬆的名字，但它是記住沒有能力的結構就像「燙手山芋」一樣，只能傳來傳去並且需要特殊處理的好方法。燙手山芋是 Move 中最強大的模式之一，我們將在 [燙手山芋模式](./../programmability/hot-potato-pattern) 章節中進行更詳細的介紹。

## 延伸閱讀

- Move 參考手冊中的 [類型能力](./../../reference/abilities)。
