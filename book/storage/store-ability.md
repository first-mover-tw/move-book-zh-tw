---
description: 儲存能力（store ability）在 Move 中允許型別被用作物件中的欄位，並在 Sui 上啟用公開轉移（public transfer）與儲存操作。
---

# 儲存能力 (Ability: Store) {#ability-store}

[`key` 能力][key-ability]要求所有欄位都必須具備 `store`，而這項要求也是理解 `store` 意義的最佳途徑：它是被_儲存_的能力——最終存在於區塊鏈狀態中的一個物件裡。具有[`copy`][copy-ability]或[`drop`][drop-ability]但沒有 `store` 的結構體，只能存活在建立它的交易期間；它永遠無法被持久化。

## 定義 (Definition) {#definition}

`store` 能力允許某型別被用作具有 `key` 能力的結構體的欄位——無論是直接使用，還是巢狀任意層數。與其他能力相同，此規則遞迴適用：一個結構體只有在其所有欄位都具備 `store` 時，才能擁有 `store`。

```move file=packages/samples/sources/storage/store-ability.move anchor=definition

```

## 與 `copy` 及 `drop` 的關係 (Relation to `copy` and `drop`) {#relation-to-copy-and-drop}

`store` 與 `copy`、`drop` 是彼此獨立的：這三種非 `key` 能力可以自由組合，彼此之間沒有蘊含關係。一個型別可以是可複製但不可儲存、可儲存但既不可複製也不可捨棄，依此類推——每種組合都是有效的，且各有其用途。

## 與 `key` 的關係 (Relation to `key`) {#relation-to-key}

一個_物件_也可以擁有 `store` 能力,而對物件而言,它扮演雙重角色:

- 具有 `store` 的物件可以被_包裝_（wrapped）:用作另一個物件的欄位。沒有 `store` 的物件則被限制永遠只能位於儲存空間的頂層。
- `store` 作為該物件的一種_公開_（public）修飾詞:它允許從_任何_模組呼叫公開的[儲存函式](./storage-functions)——`public_transfer`、`public_share_object` 以及 `public_freeze_object`。若沒有 `store`,該物件的儲存操作就只保留給定義它的模組使用,讓該模組能完全掌控此物件的移動方式。

第二項角色並非語言層級的功能,而是[Sui Framework][sui-framework]的一項慣例,透過[內部限制](./internal-constraint)來強制執行——這正是下一節的主題。是否要賦予一個物件 `store`,是 Sui 應用程式設計中最具影響力的決策之一,我們會在[儲存函式](./storage-functions#internal-rule-in-transfer-functions)一節中再次討論這個議題。

## 具有 `store` 能力的型別 (Types with the `store` Ability) {#types-with-the-store-ability}

Move 中所有原生型別（參考除外)都具有 `store` 能力。這包括:

- [bool](./../move-basics/primitive-types#booleans)
- [無號整數 (unsigned integers)](./../move-basics/primitive-types#integer-types)
- 當 `T` 具有 `store` 時的[`vector<T>`](./../move-basics/vector)
- [address](./../move-basics/address)

標準函式庫中定義的所有型別也都具有 `store` 能力。這包括:

- 當 `T` 具有 `store` 時的[`Option<T>`](./../move-basics/option)
- [String](./../move-basics/string) 與 [ASCII 字串 (ASCII String)](./../move-basics/string#ascii-strings)
- [TypeName](./../move-basics/type-reflection)

## 總結 (Summary) {#summary}

- `store` 允許某型別被持久化——在任意巢狀深度中被用作物件的欄位。
- 對物件而言,`store` 還額外解鎖了_包裝_（wrapping)以及公開的儲存函式。
- `store` 與 `copy`、`drop` 彼此獨立;容器型別是否具備 `store`,取決於其內容物是否具備此能力。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考手冊中的[型別能力 (Type Abilities)](./../../reference/abilities)。

[key-ability]: ./key-ability
[drop-ability]: ./../move-basics/drop-ability
[copy-ability]: ./../move-basics/copy-ability
[sui-framework]: ./../programmability/sui-framework
