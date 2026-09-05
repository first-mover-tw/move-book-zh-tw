---
description: Move 中的丟棄能力 (drop ability) 可讓結構 (struct) 執行個體遭到捨棄。了解其運作方式，以及何時在 Sui 智慧合約 (smart contracts) 中使用它。
title: 能力 (Abilities)：捨棄 (Drop)
keywords:
  - Move
  - Sui
  - Move tutorial
  - abilities
  - drop
questions:
  - 'What is Abilities: Drop in Move?'
  - 'How do I use Abilities: Drop in Move?'
  - When to Use drop?
  - What is Types with the drop Ability in Move?
answer: The drop ability in Move allows struct instances to be discarded. Learn how it works and when to use it in Sui smart contracts.
goal:
  description: Reader understands the drop ability in Move allows struct instances to be discarded. Learn how it works and when to use it in Sui smart contracts
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

# 能力：丟棄 (Abilities: Drop) {#abilities-drop}

在大多數程式語言中，不對某個值進行任何處理並不是問題：未使用的變數至多可能觸發警告，並會在其離開作用域的瞬間被遺忘。如同我們在 [結構 (Struct)](./struct#unpacking-a-struct) 章節所見，在 Move 中預設情況恰好相反：結構值必須被 _使用_——儲存在某處、傳遞出去，或解構——而靜默丟棄值的程式無法編譯。

`drop` 能力——四種能力中最簡單的一種——可讓你不遵守此規則。具有 `drop` 的結構可被 _忽略_ 或 _丟棄_：繫結至永不讀取的變數、以 `_` 萬用字元忽略，或在其作用域結束時直接留下。換言之，`drop` 讓 Move 型別的行為方式如同大多數其他語言中的值：

```move file=packages/samples/sources/move-basics/drop-ability.move anchor=main

```

在上述範例中，`IgnoreMe` 執行個體被指定給 `_`，且從未解構——程式碼可以編譯，因為 `IgnoreMe` 具有 `drop` 能力。`NoDrop` 執行個體無法以這種方式處理：僅有兩種選擇，保留它或解構它，而測試會在最後一行將其解構。

> `drop` 能力僅允許 _丟棄_ 值。它不允許複製或儲存值——這些行為分別由獨立的 [`copy`](./copy-ability) 與 [`store`](./../storage/store-ability) 能力管理。

## 何時使用 `drop` (When to Use `drop`) {#when-to-use-drop}

一項實用原則：`drop` 適用於表示 _資料_ 的型別；缺少它則可保護表示 _資產_ 或 _義務_ 的型別。

設定值、中繼資料、計算的中間結果——這些都不值得保護，強迫程式設計者明確銷毀每一個值只會徒增儀式感。為這類型別賦予 `drop` 能力可讓程式碼保持簡潔。集合型別是很好的範例：由於 `vector` 具有 `drop`（當其內容也具有時），不再需要的數字向量可以直接被遺忘。

另一方面，缺少 `drop` 是 Move 型別系統的定義性特徵之一。硬幣、票券、收據、償還義務——這類值絕不可靜默消失，而不具備 `drop` 的型別可在編譯器層級提供此保證：持有該值的人會被 _強制_ 對其進行有意義的處理。由編譯器強制處理值，是[熱馬鈴薯模式 (Hot Potato pattern)](./../programmability/hot-potato-pattern) 的基礎；該模式已在[前一節 (previous section)](./abilities-introduction#no-abilities) 提及，而我們會在[所有權與作用域 (Ownership and Scope)](./ownership-and-scope) 章節中探討值如何在作用域之間移動的完整規則。

> 僅具有 `drop` 一種能力的結構稱為 _Witness_。我們會在[見證與抽象實作 (Witness and Abstract Implementation)](./../programmability/witness-pattern) 章節中說明 _Witness_ 的概念。

## 具有 `drop` 能力的型別 (Types with the `drop` Ability) {#types-with-the-drop-ability}

Move 中所有原生型別都具有 `drop` 能力。包括：

- [`bool`](./../move-basics/primitive-types#booleans)
- [無號整數](./../move-basics/primitive-types#integer-types)
- 當 `T` 具有 `drop` 時的 [`vector<T>`](./../move-basics/vector)
- [`address`](./../move-basics/address)

標準函式庫中定義的所有型別也都具有 `drop` 能力。包括：

- 當 `T` 具有 `drop` 時的 [`Option<T>`](./../move-basics/option)
- [`String`](./../move-basics/string)
- [`TypeName`](./../move-basics/type-reflection)

請注意清單中的模式：如 `vector` 或 `Option` 的容器型別，只有在其內容可被丟棄時才能被丟棄。若向量中的元素受到保護而不可丟棄，持有它們的向量也會受到保護——否則丟棄容器將成為丟棄其內容的漏洞。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[型別能力 (Type Abilities)](./../../reference/abilities)。
