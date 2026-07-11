---
description: Move 能力 (abilities) 簡介：copy、drop、key 與 store — 這套系統控制型別在智能合約中的行為方式。
---

# 能力：簡介 (Abilities: Introduction) {#abilities-introduction}

Move 有一個獨特的型別系統，每個型別都會宣告其值被允許做什麼。在
[前一節](./struct) 中，每個 `Artist` 和 `Record` 的實例都必須被使用：儲存、傳遞下去，或解構——捨棄一個值，或複製它，都不是選項。這並非偶然的嚴格性。預設情況下，一個 Move 值只能被建立、傳遞，以及拆解；除此之外的一切都是型別必須明確被授予的特權。這些特權稱為 _能力（abilities）_。

## 什麼是能力？ (What are Abilities?) {#what-are-abilities}

能力是型別上的權限。它們作為 struct 定義的一部分被宣告，編譯器會拒絕該型別不被允許執行的任何操作。能力本身不會為型別新增任何功能——它只是解鎖了原本會是編譯錯誤的行為。

Move 中有四種能力。其中兩種控制在執行期間值可以發生什麼事：

- `copy` - 該值可以被 _複製_；
- `drop` - 該值可以被 _捨棄_；

另外兩種控制儲存：

- `key` - 該值可以作為儲存的單位——在 Sui 上，即為一個 _object_；
- `store` - 該值可以被儲存 _在_ 儲存中的其他值 _內部_。

這種「預設拒絕」的設計，正是讓 Move 型別能夠忠實地建模資產的原因：沒有 `copy` 的型別不能被複製，沒有 `drop` 的型別不能遺失——這是一個具有普通、可自由複製值的語言無法給予的保證。

> 在本書中，你會看到名為 `能力：<名稱>` 的章節，各自詳細涵蓋一種能力：它如何運作，以及何時該使用它。

## 能力語法 (Abilities Syntax) {#abilities-syntax}

能力是在 struct 定義中使用 `has` 關鍵字，後面接以逗號分隔的能力列表來設定：

```move file=packages/samples/sources/move-basics/abilities-introduction.move anchor=definition

```

這兩個被宣告的能力改變了 `VeryAble` 實例的行為方式。把以下程式碼與[前一節](./struct)中的打包與解包儀式做比較：

```move file=packages/samples/sources/move-basics/abilities-introduction.move anchor=use

```

現在，讓我們快速逐一巡覽這四種能力。

## `drop`：捨棄值 (`drop`: Discarding Values) {#drop-discarding-values}

`drop` 能力允許一個實例被 _捨棄_：賦值給一個未使用的變數、以萬用字元 `_` 忽略，或在作用域結束時單純被留下不管。換句話說，`drop` 讓一個型別的行為表現得像大多數其他程式語言中的值一樣。它適用於代表純粹 _資料_ 的型別，而它的缺席則保護了代表 _資產_ 的型別。[下一節](./drop-ability) 專門討論它。

## `copy`：複製值 (`copy`: Duplicating Values) {#copy-duplicating-values}

`copy` 能力允許一個實例被 _複製_，可以由編譯器隱式完成，或以 `copy` 關鍵字顯式完成。所有的原始型別——整數、`bool`、`address`——的行為都彷彿具有這個能力。請注意，`copy` 幾乎總是與 `drop` 一起出現：一個可以被複製但不能被捨棄的值，會強迫它的每一份副本都必須被使用。詳細內容涵蓋在[能力：Copy](./copy-ability) 一節中。

## `key`：物件與儲存 (`key`: Objects and Storage) {#key-objects-and-storage}

`key` 能力將一個型別標記為 _儲存的單位_：一個實例可以被寫入區塊鏈狀態，並之後透過其唯一識別碼——也就是它的「key」——被找到。在 Sui 上，具有 `key` 能力的 struct 稱為 _object_，而且它被要求要有 `id: UID` 作為其第一個欄位。物件是 Sui 程式設計模型的核心，整個 [物件模型](./../object/) 章節都專門討論它們，接著是 [能力：Key](./../storage/key-ability) 涵蓋這個能力本身。

## `store`：儲存在物件內部 (`store`: Storing Inside Objects) {#store-storing-inside-objects}

`store` 能力允許一個實例被儲存 _在_ 其他最終進入儲存中的 struct _內部_。`key` 讓一個型別成為區塊鏈狀態中的頂層記錄，而 `store` 則允許一個型別成為其中的 _一部分_。這在 [能力：Store](./../storage/store-ability) 一節中有解說。

## 能力來自於欄位 (Abilities Come from Fields) {#abilities-come-from-fields}

一種能力是關於整個值（包括其內容）的承諾——所以一個 struct 只能被授予其所有欄位型別都支援的能力。具有 `copy` 的 struct 要求每個欄位都要有 `copy`，`drop` 和 `store` 也是同樣的道理；`key` 則要求每個欄位都要有 `store`。編譯器會在定義處強制執行這一點，以下程式碼將無法編譯：

```move
public struct NoAbilities {}

public struct Wrapper has copy, drop {
    inner: NoAbilities,
    //     ^ 錯誤！這個 struct 宣告了能力 'copy'
    //       所以所有欄位都需要能力 'copy'
}
```

> 除了[參照](./references)以外的所有內建型別都具有 `copy`、`drop` 和 `store` 能力，而參照具有 `copy` 和 `drop`。容器型別如 [`vector`](./vector) 和 [`Option`](./option) _有條件地_ 支援 `copy`、`drop` 和 `store`——一個 vector 只有在其元素可以被複製的情況下才能被複製。

## 沒有能力 (No Abilities) {#no-abilities}

一個沒有任何能力的 struct 不能被捨棄、複製，或儲存在儲存中。我們稱這樣的 struct 為 _燙手山芋（Hot Potato）_。這是一個輕鬆的名稱，但它是記住「沒有能力的 struct」的好方法——它就像一顆燙手山芋，只能被傳來傳去，並需要特別的處理方式。Hot Potato 是 Move 中最強大的模式之一，我們會在 [Hot Potato 模式](./../programmability/hot-potato-pattern) 章節中更詳細地說明。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考手冊中的[型別能力](./../../reference/abilities)。
