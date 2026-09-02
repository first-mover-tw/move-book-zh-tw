---
description: 拋棄能力 (drop ability)
---

# Abilities：Drop 能力 (Abilities: Drop) {#abilities-drop}

在大多數程式語言中，不對一個值做任何事並不是問題：未使用的變數頂多觸發一個警告，一旦離開作用域就會被遺忘。在 Move 中，正如我們在 [Struct](./struct#unpacking-a-struct) 章節看到的，預設行為恰恰相反：struct 值必須被*使用*——儲存在某處、傳遞下去，或被拆解——而一個默默丟棄某個值的程式無法通過編譯。

`drop` 能力——四種能力中最簡單的一個——是這條規則的選擇退出機制。擁有 `drop` 的 struct 可以被*忽略*或*丟棄*：綁定到一個永遠不會被讀取的變數、用 `_` 萬用字元忽略，或是在其作用域結束時單純被留下不管。換句話說，`drop` 讓 Move 型別的行為就像大多數其他語言中的值一樣：

```move file=packages/samples/sources/move-basics/drop-ability.move anchor=main

```

在上面的範例中，`IgnoreMe` 實例被指派給 `_` 且從未被拆解——程式碼可以編譯，因為 `IgnoreMe` 擁有 `drop` 能力。`NoDrop` 實例不能這樣處理：唯一的兩個選項是保留它或拆解它，而測試在最後一行拆解了它。

> `drop` 能力只允許*丟棄*一個值。它不允許複製或儲存該值——這些行為分別由獨立的 [`copy`](./copy-ability) 與 [`store`](./../storage/store-ability) 能力所管控。

## 何時使用 `drop` (When to Use `drop`) {#when-to-use-drop}

一個不錯的經驗法則：`drop` 應該屬於代表*資料*的型別，而它的缺席則保護了代表*資產*或*義務*的型別。

設定值、中繼資料、運算的中間結果——這些都不值得被保護，強迫程式設計師明確銷毀每一個都純屬形式。賦予這類型別 `drop` 能力能讓程式碼保持簡潔。集合型別就是一個很好的例子：因為 `vector` 擁有 `drop`（當其內容也擁有時），一個數字的 vector 在不再需要時可以直接被遺忘。

另一方面，缺少 `drop` 是 Move 型別系統的核心特徵之一。一枚代幣、一張票券、一張收據、一個償還義務——像這樣的值絕不能默默消失，而沒有 `drop` 的型別在編譯器層級保證了這一點：無論誰持有該值，都會被*強迫*對它做出有意義的處理。編譯器強制執行的值處理，正是[前一節](./abilities-introduction#no-abilities)提到的 [Hot Potato 模式](./../programmability/hot-potato-pattern)的基礎，我們將在 [Ownership and Scope](./ownership-and-scope) 章節探討值如何在作用域之間移動的完整規則。

> 一個只擁有 `drop` 作為單一能力的 struct 稱為 _Witness_。我們會在 [Witness and Abstract Implementation](./../programmability/witness-pattern) 章節解釋 _Witness_ 的概念。

## 擁有 `drop` 能力的型別 (Types with the `drop` Ability) {#types-with-the-drop-ability}

Move 中所有原生型別都擁有 `drop` 能力。這包括：

- [`bool`](./../move-basics/primitive-types#booleans)
- [無號整數](./../move-basics/primitive-types#integer-types)
- 當 `T` 擁有 `drop` 時的 [`vector<T>`](./../move-basics/vector)
- [`address`](./../move-basics/address)

標準函式庫中定義的所有型別同樣擁有 `drop` 能力。這包括：

- 當 `T` 擁有 `drop` 時的 [`Option<T>`](./../move-basics/option)
- [`String`](./../move-basics/string)
- [`TypeName`](./../move-basics/type-reflection)

請注意這份清單中的模式：像 `vector` 或 `Option` 這樣的容器型別，只有在其內容可以被丟棄時才能被丟棄。如果 vector 的元素被保護而無法丟棄，那麼持有它們的 vector 也會受到保護——否則丟棄容器就會成為丟棄其內容的漏洞。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的 [Type Abilities](./../../reference/abilities)。
