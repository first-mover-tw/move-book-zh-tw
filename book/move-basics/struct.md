---
description: 使用結構 (struct) 在 Move 中定義自訂型別 (custom types)：在 Sui 智慧合約 (smart contracts) 中打包 (pack)、解包 (unpack)、存取欄位 (fields)，並使用取得器 (getters) 與設定器 (setters) 控制欄位可見性 (field visibility)。
title: 使用結構 (Struct) 的自訂型別
keywords:
  - Move
  - Sui
  - Move tutorial
  - custom
  - types
  - struct
  - type system
questions:
  - What is Custom Types with Struct in Move?
  - How do I use Custom Types with Struct in Move?
  - What is Defining a Struct in Move?
  - What is Creating an Instance in Move?
answer: 'Define custom types with struct in Move: pack, unpack, access fields, and control field visibility with getters and setters in Sui smart contracts.'
goal:
  description: 'Reader can define custom types with struct in Move: pack, unpack, access fields, and control field visibility with getters and setters in Sui smart contracts'
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

# 使用 Struct 的自訂型別 (Custom Types with Struct) {#custom-types-with-struct}

_struct_ 是一種由使用者定義的型別，可將相關的值群組為單一單位，並為群組及其內部的每個值命名。如果你熟悉物件導向語言，struct 類似於物件的資料屬性。應用程式不必分別傳遞鬆散的標題、藝術家與發行年份，而是可以定義 `Record` 型別，並將這三者作為一個值處理。

自訂型別是 Move 程式的骨幹：它們描述應用程式的資料，而且——如後續章節所示——定義型別的模組會控制可對其值執行的一切操作。本節將介紹 struct 的定義及其使用方式。

## 定義 Struct (Defining a Struct) {#defining-a-struct}

若要定義自訂型別，請使用 `public struct` 關鍵字，後接型別名稱與欄位區塊。每個欄位都以 `field_name: field_type` 語法定義，且欄位定義必須以逗號分隔。欄位可以是任何型別，包括其他 struct。

> Move 不支援遞迴 struct，也就是 struct 不能將自身作為欄位。

```move file=packages/samples/sources/move-basics/struct.move anchor=def

```

在上方範例中，我們定義了一個具有單一欄位的 `Artist` struct，以及一個具有五個欄位的 `Record` struct。`title` 欄位的型別為 [`String`](./string)，`artist` 欄位使用我們剛定義的自訂 `Artist` 型別，`year` 欄位的型別為 `u16`，`is_debut` 欄位的型別為 `bool`，而 `edition` 欄位的型別為 [`Option<u16>`](./option)，用以表示版本為選用項目。

`String` 型別並非語言內建——它定義於[標準函式庫](./standard-library)，並透過範例頂端的 `use` 陳述式帶入作用域；匯入功能會在[匯入模組](./importing-modules)章節中說明。`Option<u16>` 中的角括號表示一個 _型別參數_：`Option<u16>` 是持有 `u16` 的 `Option`。型別參數會在[泛型](./generics)章節中說明。

> Struct 定義也可以宣告 _abilities_——可放寬型別值預設限制的屬性。它們以 `has` 關鍵字列出，可置於欄位之前——`public struct Foo has copy, drop { ... }`——或置於欄位之後並以分號結尾——`public struct Foo { ... } has copy, drop;`。abilities 會在[能力簡介](./abilities-introduction)章節中介紹。

## 建立執行個體 (Creating an Instance) {#creating-an-instance}

我們已說明 struct 的*定義*。現在來看看如何建立其執行個體。建立 struct 執行個體稱為 _packing_，使用 `StructName { field1: value1, field2: value2, ... }` 語法完成。欄位可依任意順序設定，但必須全部設定——struct 無法部分初始化。

> 本頁的範例位於與定義 struct 相同模組中的[測試函式](./testing)內——如同即將看到的內容，struct 只能在其模組內建立與拆解。全篇使用的 `assert_eq!` 是一個 _macro_——因此名稱中有 `!`——它會比較兩個值，若不同則失敗；其內容會在[測試](./testing)章節中說明。

```move file=packages/samples/sources/move-basics/struct.move anchor=pack

```

在上方範例中，我們建立 `Artist` struct 的執行個體，並將 `name` 欄位設為字串 "The Beatles"。值 `"The Beatles"` 是一個 _字串字面值_：編譯器看見 `name` 欄位預期為 `String`，便會自動推斷字面值的型別。字串會在[字串](./string)章節中更詳細說明。

Move 也提供簡寫：若區域變數與欄位名稱相同，欄位名稱只需給定一次。這稱為 _field name punning_。

```move file=packages/samples/sources/move-basics/struct.move anchor=pack_shorthand

```

## 存取欄位 (Accessing Fields) {#accessing-fields}

若要存取 struct 的欄位，請使用 `.`（點）運算子，後接欄位名稱。欄位可以讀取；若變數以 `mut` 宣告，則可指派新值。

```move file=packages/samples/sources/move-basics/struct.move anchor=access

```

以此方式存取欄位，只能在定義 struct 的模組中運作。為了理解原因，讓我們更仔細看看 struct 的可見性。

## 欄位可見性 (Field Visibility) {#field-visibility}

你可能已注意到，每個 struct 都以 `public` 修飾詞宣告——這是必要的，若未加以宣告會造成編譯錯誤。`public` 修飾詞讓 struct *型別*對其他模組可見：它可被[匯入](./importing-modules)、用於型別定義及函式簽名。

不過，struct 的*內容*永遠都會保留在定義它的模組內。不同於某些語言，Move 沒有逐欄位的可見性修飾詞——無法將欄位標記為 public。在定義模組之外，不可能：

- 讀取或寫入 struct 的欄位；
- 建立（「pack」）struct 的執行個體；
- 銷毀（「unpack」）struct 的執行個體。

這是一項特性，而非限制。這表示模組可完整控制其型別的建立、使用與銷毀方式，且任何外部原始碼都無法違反模組設定的規則。在[物件模型](./../object/)章節中，我們會說明如何利用此特性建立資產模型，並對其強制執行保證。

> 請注意，struct 欄位無法從其他模組存取，並不代表其值具備機密性——始終可從 Move 外部讀取鏈上物件的內容。你絕不可在物件中儲存未加密的秘密資訊。

## Getter 與 Setter (Getters and Setters) {#getters-and-setters}

由於欄位只能在定義模組內存取，若其他模組應可讀取或更新它們，該模組便需要公開函式。回傳欄位值的函式慣例上稱為 _getter_，而更新欄位的函式則稱為 _setter_。

getter 通常接受 struct 的[參考](./references)，並回傳欄位值：

```move file=packages/samples/sources/move-basics/struct.move anchor=getter

```

setter 接受 struct 的可變參考與新值：

```move file=packages/samples/sources/move-basics/struct.move anchor=setter

```

接著可使用 `.` 運算子呼叫這兩個函式，如同存取欄位：

```move file=packages/samples/sources/move-basics/struct.move anchor=getter_setter_use

```

由於這些函式是 `public`，任何匯入 `Artist` 的模組都能呼叫它們。請注意括號：`artist.name()` 是函式呼叫，只要函式可見便可在任何位置運作；而欄位存取 `artist.name` 則無法在定義模組外編譯。

> `public fun` 語法定義公開函式；函式會在[函式](./function)章節中詳細說明。簽名中的 `&` 與 `&mut` 是參考——它們讓函式可讀取或修改值，而不取得其所有權。我們會在[參考](./references)章節中說明它們，並在[Struct 方法](./struct-methods)章節中說明點呼叫語法。

雖然 getter 非常常見，但 setter 較少定義，且通常會附帶額外檢查。選擇公開哪些函式，正是定義型別介面的方式——模組決定外部原始碼可對其 struct 執行與不可執行的操作。

## 拆解 Struct (Unpacking a Struct) {#unpacking-a-struct}

Struct 預設不可丟棄：struct 值不能只是在函式結尾被遺留——這樣的原始碼無法編譯。每個建立的值都必須被使用：不是儲存（例如放入另一個 struct，或如[使用物件](./../storage/)章節所示保留於鏈上儲存空間），就是 _unpacked_。拆解 struct 表示將其解構為欄位，且它是 packing 的鏡像操作：使用 `let` 關鍵字，後接 struct 名稱與要繫結的欄位名稱。

```move file=packages/samples/sources/move-basics/struct.move anchor=unpack

```

在上方範例中，我們拆解 `Artist` struct，並建立一個新變數 `name`，其值為 `name` 欄位的值。此行之後，struct 值不再存在——它已被拆分為各個部分。

如果不需要某個欄位，可以將其繫結至底線 `_` 來忽略它。然而，由於 struct 本身無法丟棄，模式中仍必須列出其所有欄位：

```move file=packages/samples/sources/move-basics/struct.move anchor=unpack_ignore

```

對於具有許多欄位的 struct，列出每個忽略的欄位會很冗長。`..` 模式——_rest_ 模式——可一次比對所有剩餘欄位：

```move file=packages/samples/sources/move-basics/struct.move anchor=unpack_rest

```

在上方範例中，我們 pack 一個完整的 `Record`——`option::none()` 呼叫會建立空的 `Option` 值，請參閱 [Option](./option) 章節——然後將其 unpack，保留 `title` 與 `artist` 欄位，並以 `..` 忽略其餘欄位。

請注意，忽略欄位——不論使用 `_` 或 `..`——都會丟棄其值，這僅允許用於可丟棄的值。`String`、`u16` 與 `bool` 等簡單值可自由丟棄，但 `Artist` 不行——因此範例也會拆解 `artist` 繫結，而非忽略它。哪些值可丟棄、哪些不可，由 _abilities_ 決定；後續章節會說明：[能力簡介](./abilities-introduction)與 [Ability: Drop](./drop-ability)。

## 位置 Struct (Positional Structs) {#positional-structs}

至今，本頁的每個 struct 都有具名欄位。Move 也支援 _positional_ struct，其欄位沒有名稱，而是以位置識別。位置 struct 以括號而非大括號定義，且定義沒有主體——它會在欄位清單後立即結束：

```move file=packages/samples/sources/move-basics/struct.move anchor=positional_def

```

abilities 同樣可置於欄位之前或之後；在後置形式中，它們位於括號之後：`public struct Duration(u64, u64) has copy, drop;`。

位置 struct 同樣使用括號進行 packing 與 unpacking，並以 `.` 運算子後接欄位索引來存取欄位，索引從零開始：

```move file=packages/samples/sources/move-basics/struct.move anchor=positional_use

```

當欄位名稱無法為型別名稱已表達的內容增加資訊時，位置 struct 是合適的選擇——通常用於含有一或兩個欄位的小型包裝型別。本頁所述的所有規則仍適用於它們：欄位只能在定義模組內存取，且值必須被使用——儲存或拆解。對於具有更多欄位的 struct，具名欄位通常是較佳選擇。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的 [Structs](./../../reference/structs)。
