---
description: Move (Move) 中的 store (store) 能力可讓類型 (types) 用作物件 (objects) 的欄位，並在 Sui 上啟用公開轉移與儲存操作。
title: 能力：儲存 (Store)
keywords:
  - Move
  - Sui
  - Move tutorial
  - ability
  - store
  - abilities
  - storage
questions:
  - 'What is Ability: Store in Move?'
  - 'How do I use Ability: Store in Move?'
  - What is Definition in Move?
  - What is Relation to copy and drop in Move?
answer: The store ability in Move allows types to be used as fields in objects and enables public transfer and storage operations on Sui.
goal:
  description: Reader understands the store ability in Move allows types to be used as fields in objects and enables public transfer and storage operations on Sui
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

# 能力：儲存 (Ability: Store) {#ability-store}

[`key` 能力][key-ability]要求所有欄位都具有 `store`，而這項要求是理解 `store` 意義的最佳方式：它是可被*儲存*的能力——最終可存在於區塊鏈狀態中的物件內。具有 [`copy`][copy-ability] 或 [`drop`][drop-ability]、但不具有 `store` 的結構只能在建立它的交易期間存在；它永遠無法被持久化。

## 定義 (Definition) {#definition}

`store` 能力允許型別作為具有 `key` 能力之結構的欄位使用——可直接使用，或巢狀於任意深度。與其他能力相同，此規則會遞迴套用：只有當結構的所有欄位都具有 `store` 時，該結構才能具有 `store`。

```move file=packages/samples/sources/storage/store-ability.move anchor=definition

```

## 與 `copy` 和 `drop` 的關係 (Relation to `copy` and `drop`) {#relation-to-copy-and-drop}

`store` 與 `copy` 和 `drop` 彼此獨立：三種非 `key` 能力可自由組合，且沒有任何一種意味著另一種。型別可以可複製但不可儲存、可儲存但既不可複製也不可丟棄，依此類推——每種組合都有效且各有用途。

## 與 `key` 的關係 (Relation to `key`) {#relation-to-key}

*物件*也可以具有 `store` 能力，對物件而言，它扮演雙重角色：

- 具有 `store` 的物件可被*包裝*：作為另一個物件的欄位使用。沒有 `store` 的物件受限於必須始終位於儲存空間的最上層。
- `store` 會作為物件的*公開*修飾詞：它允許從*任何*模組呼叫公開的[儲存函式](./storage-functions)——`public_transfer`、`public_share_object` 和 `public_freeze_object`。若沒有 `store`，物件的儲存操作將保留給其定義模組，使該模組能完全控制物件的移動方式。

第二個角色不是語言功能，而是 [Sui Framework][sui-framework] 的慣例，透過[內部限制](./internal-constraint)強制執行——這是下一節的主題。是否為物件賦予 `store`，是 Sui 應用程式中影響最深遠的設計決策之一；我們會在[儲存函式](./storage-functions#internal-rule-in-transfer-functions)中再次討論它。

## 具有 `store` 能力的型別 (Types with the `store` Ability) {#types-with-the-store-ability}

Move 中所有原生型別（參考除外）都具有 `store` 能力。包括：

- [bool](./../move-basics/primitive-types#booleans)
- [無符號整數](./../move-basics/primitive-types#integer-types)
- 當 `T` 具有 `store` 時的 [`vector<T>`](./../move-basics/vector)
- [address](./../move-basics/address)

標準函式庫中定義的所有型別也都具有 `store` 能力。包括：

- 當 `T` 具有 `store` 時的 [`Option<T>`](./../move-basics/option)
- [String](./../move-basics/string) 與 [ASCII String](./../move-basics/string#ascii-strings)
- [TypeName](./../move-basics/type-reflection)

## 總結 (Summary) {#summary}

- `store` 允許型別被持久化——作為物件的欄位使用，且可位於任意巢狀深度。
- 對物件而言，`store` 另外啟用*包裝*與公開儲存函式。
- `store` 與 `copy` 和 `drop` 彼此獨立；容器型別是否具有它取決於其內容。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[型別能力](./../../reference/abilities)。

[key-ability]: ./key-ability
[drop-ability]: ./../move-basics/drop-ability
[copy-ability]: ./../move-basics/copy-ability
[sui-framework]: ./../programmability/sui-framework
