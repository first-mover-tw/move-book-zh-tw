---
description: Move 能力 (abilities) 簡介：copy、drop、key 與 store——控制型別在智慧合約中行為的系統。
title: 能力 (Abilities)：簡介
keywords:
  - Move
  - Sui
  - Move tutorial
  - abilities
  - introduction
questions:
  - 'What is Abilities: Introduction in Move?'
  - 'How do I use Abilities: Introduction in Move?'
  - What are Abilities?
  - What is Abilities Syntax in Move?
answer: 'Introduction to Move abilities: copy, drop, key, and store — the system that controls how types behave in smart contracts.'
goal:
  description: 'Reader understands introduction to Move abilities: copy, drop, key, and store — the system that controls how types behave in smart contracts'
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

# 能力：簡介 (Abilities: Introduction) {#abilities-introduction}

Move 有一套獨特的型別系統，其中每個型別會宣告其值允許執行的操作。在[上一節](./struct)中，每個 `Artist` 與 `Record` 執行個體都必須被使用：儲存、傳遞或解構——捨棄或複製值都不是可行選項。這不是刻意的嚴格限制。預設情況下，Move 值只能被建立、移動與拆解；超出這些範圍的操作，都是型別必須明確獲得的權限。這些權限稱為「_能力_」（abilities）。

## 什麼是能力？ (What are Abilities?) {#what-are-abilities}

能力是型別所具備的權限。它們會作為 struct 定義的一部分被宣告，編譯器會拒絕型別未獲准執行的任何操作。能力不會為型別本身增加任何功能——它會解鎖原本會造成編譯錯誤的行為。

Move 有四種能力。其中兩種控制值在執行期間可以發生什麼事：

- `copy` - 值可以被*複製*；
- `drop` - 值可以被*捨棄*；

另兩種則控制儲存：

- `key` - 值可以作為儲存單位——在 Sui 上即為*物件*；
- `store` - 值可以儲存在其他位於儲存空間中的值*內部*。

這種「預設拒絕」的設計，讓 Move 型別能忠實地建模資產：沒有 `copy` 的型別無法被複製，沒有 `drop` 的型別也不會遺失——這些保證是具有一般可自由複製值的語言無法提供的。

> 在本書中，你會看到名為 `Ability: <name>` 的章節，各自詳細說明一種能力：其運作方式與使用時機。

## 能力語法 (Abilities Syntax) {#abilities-syntax}

能力會使用 `has` 關鍵字，在 struct 定義中以逗號分隔的能力清單設定：

```move file=packages/samples/sources/move-basics/abilities-introduction.move anchor=definition

```

這兩項已宣告的能力會改變 `VeryAble` 執行個體的行為。請將下列程式碼與[上一節](./struct)中的封裝與解構流程比較：

```move file=packages/samples/sources/move-basics/abilities-introduction.move anchor=use

```

現在，讓我們依序快速了解全部四種能力。

## `drop`：捨棄值 (`drop`: Discarding Values) {#drop-discarding-values}

`drop` 能力允許執行個體被*捨棄*：指派給未使用的變數、使用 `_` 萬用字元忽略，或在作用域結束時直接遺留。換句話說，`drop` 讓型別的行為如同多數其他程式語言中的值。它適用於代表一般*資料*的型別；缺少它則可保護代表*資產*的型別。[下一節](./drop-ability)專門說明此能力。

## `copy`：複製值 (`copy`: Duplicating Values) {#copy-duplicating-values}

`copy` 能力允許執行個體被*複製*，可以由編譯器隱式複製，或使用 `copy` 關鍵字明確複製。所有原始型別——整數、`bool`、`address`——都如同具備此能力。請注意，`copy` 幾乎總是與 `drop` 一同出現：能複製卻不能捨棄的值，會強迫其每一份複本都必須被使用。詳細內容請見[能力：複製](./copy-ability)章節。

## `key`：物件與儲存 (`key`: Objects and Storage) {#key-objects-and-storage}

`key` 能力將型別標示為*儲存單位*：執行個體可以寫入區塊鏈狀態，並透過其唯一識別碼——也就是它的「key」——在之後找到。在 Sui 上，具有 `key` 能力的 struct 稱為*物件*，且第一個欄位必須為 `id: UID`。物件是 Sui 程式設計模型的核心，完整的[物件模型](./../object/)章節專門說明物件，後續還有[能力：鍵](./../storage/key-ability)說明此能力本身。

## `store`：儲存於物件內 (`store`: Storing Inside Objects) {#store-storing-inside-objects}

`store` 能力允許執行個體儲存在其他最終會進入儲存空間的 struct _內部_。`key` 讓型別成為區塊鏈狀態中的頂層記錄，而 `store` 則允許型別成為其中的*一部分*。詳情請見[能力：儲存](./../storage/store-ability)章節。

## 能力來自欄位 (Abilities Come from Fields) {#abilities-come-from-fields}

能力是對整個值（包含其內容）的承諾，因此 struct 只有在其所有欄位型別都支援時，才能被賦予某項能力。具有 `copy` 的 struct 要求每個欄位都具備 `copy`；`drop` 與 `store` 也是如此；`key` 則要求每個欄位都具備 `store`。編譯器會在定義處強制執行此規則，因此下列程式碼無法編譯：

```move
public struct NoAbilities {}

public struct Wrapper has copy, drop {
    inner: NoAbilities,
    //     ^ 錯誤！此 struct 已宣告具備 'copy' 能力
    //       因此所有欄位都必須具備 'copy' 能力
}
```

> 除了[參考](./references)以外，所有內建型別都具有 `copy`、`drop` 與 `store` 能力；參考則具有 `copy` 與 `drop`。如 [`vector`](./vector) 與 [`Option`](./option) 等容器型別會*有條件地*支援 `copy`、`drop` 與 `store`——vector 只有在其元素可以被複製時才能被複製。

## 無能力 (No Abilities) {#no-abilities}

沒有能力的 struct 無法被捨棄、複製或儲存在儲存空間中。我們將這類 struct 稱為*燙手山芋*（Hot Potato）。這是個輕鬆的名稱，但有助於記住：沒有能力的 struct 就像燙手山芋——只能被傳遞，且需要特殊處理。燙手山芋是 Move 中最強大的模式之一；我們會在[燙手山芋模式](./../programmability/hot-potato-pattern)章節中更深入說明。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[型別能力](./../../reference/abilities)。
