---
description: 定義自訂結構體 (struct)：於 Sui 智慧合約中打包 (pack)、拆解 (unpack)、存取欄位，並用 getter 與 setter 控制欄位可見性
---

# 用結構體自訂型別 (Custom Types with Struct) {#custom-types-with-struct}

_struct_（結構體）是一種使用者自訂型別，將相關的值群組成單一單元，同時為這個群組和其中每個值命名。如果你熟悉物件導向語言，struct 類似於物件的資料屬性。與其分別傳遞鬆散的 title、artist 和 release year，應用程式可以定義一個 `Record` 型別，將這三者當作一個值來處理。

自訂型別是 Move 程式的骨幹：它們描述應用程式的資料，而且——後續章節會說明——定義某型別的模組控制了該型別值上能做的一切事情。本節將介紹 struct 的定義方式與使用方法。

## 定義結構體 (Defining a Struct) {#defining-a-struct}

要定義自訂型別，使用 `public struct` 關鍵字，後面接型別名稱，以及一個欄位區塊。每個欄位以 `field_name: field_type` 語法定義，欄位定義之間必須用逗號分隔。欄位可以是任何型別，包括其他 struct。

> Move 不支援遞迴結構體，也就是說一個 struct 不能將自己作為欄位包含在內。

```move file=packages/samples/sources/move-basics/struct.move anchor=def

```

在上面的範例中,我們定義了一個只有一個欄位的 `Artist` struct,以及一個有五個欄位的 `Record` struct。`title` 欄位型別為 [`String`](./string)、`artist` 欄位使用我們剛定義的自訂型別 `Artist`、`year` 欄位型別為 `u16`、`is_debut` 欄位型別為 `bool`、`edition` 欄位型別為 [`Option<u16>`](./option),用來表示 edition 是可選的。

`String` 型別並非內建於語言中——它定義在[標準函式庫](./standard-library)中,並透過範例最上方的 `use` 陳述式引入到作用域內;匯入的內容在[匯入模組 (Importing Modules)](./importing-modules)一節中說明。`Option<u16>` 中的角括號代表一個 _type parameter_(型別參數):`Option<u16>` 是一個持有 `u16` 的 `Option`。型別參數在[泛型 (Generics)](./generics)一節中說明。

> struct 定義也可以宣告 _abilities_(能力)——放寬該型別值上預設限制的屬性。它們以 `has` 關鍵字列出,可以放在欄位之前——`public struct Foo has copy, drop { ... }`——或放在欄位之後,以分號結尾——`public struct Foo { ... } has copy, drop;`。abilities 在[能力介紹 (Abilities Introduction)](./abilities-introduction)一節中介紹。

## 建立實例 (Creating an Instance) {#creating-an-instance}

我們已經描述了 struct 的 _定義_。現在來看看如何建立一個實例。建立 struct 的實例稱為 _packing_(打包),透過 `StructName { field1: value1, field2: value2, ... }` 語法完成。欄位可以以任意順序設定,但全部欄位都必須設定——struct 不能只被部分初始化。

> 本頁的範例都放在同一個定義這些 struct 的模組中的一個[測試函式 (test function)](./testing)內——我們接下來會看到,struct 只能在其所屬模組內建立與拆解。全篇使用的 `assert_eq!` 是一個 _macro_(巨集)——因此名稱中有 `!`——用來比較兩個值,若不相等則失敗;在[測試 (Testing)](./testing)一節中說明。

```move file=packages/samples/sources/move-basics/struct.move anchor=pack

```

在上面的範例中,我們建立了 `Artist` struct 的一個實例,並將 `name` 欄位設為字串 "The Beatles"。值 `"The Beatles"` 是一個 _字串字面值 (string literal)_:編譯器看到 `name` 欄位預期是 `String`,並自動推斷字面值的型別。字串在[String](./string)一節中有更詳細的說明。

Move 還提供一種簡寫:如果一個區域變數的名稱與欄位名稱相同,欄位名稱只需寫一次即可。這稱為 _欄位名稱雙關 (field name punning)_。

```move file=packages/samples/sources/move-basics/struct.move anchor=pack_shorthand

```

## 存取欄位 (Accessing Fields) {#accessing-fields}

要存取 struct 的欄位,使用 `.`(點)運算子加上欄位名稱。欄位可以被讀取,若該變數宣告為 `mut`,也可以被指派新值。

```move file=packages/samples/sources/move-basics/struct.move anchor=access

```

這種存取欄位的方式只在定義該 struct 的模組內有效。要理解原因,讓我們更仔細看看 struct 的可見性。

## 欄位可見性 (Field Visibility) {#field-visibility}

你可能已經注意到,每個 struct 都以 `public` 修飾詞宣告——這是必須的,若沒有它就會導致編譯錯誤。`public` 修飾詞使該 struct _型別_ 對其他模組可見:它可以被[匯入](./importing-modules)、用於型別定義,以及用於函式簽章中。

然而,struct 的 _內容_ 永遠只在定義它的模組內部可見。與某些語言不同,Move 沒有逐欄位的可見性修飾詞——沒有辦法把某個欄位標示為公開。在定義模組之外,不可能做到:

- 讀取或寫入 struct 的欄位;
- 建立(「打包」)struct 的實例;
- 銷毀(「拆解」)struct 的實例。

這是一項特性,而非限制。它意味著模組完全掌控其型別如何被建立、使用與銷毀,任何外部程式碼都無法違反該模組所設下的規則。在[物件模型 (Object Model)](./../object/)章節中,我們會展示這項特性如何被用來塑模資產並對其強制保證。

> 請注意,雖然 struct 的欄位無法從其他模組存取,但這不代表它的值是機密的——從 Move 外部隨時都能讀取鏈上物件的內容。你絕對不應該在物件中儲存未加密的機密。

## Getter 和 Setter (Getters and Setters) {#getters-and-setters}

由於欄位只能在定義模組內部存取,如果其他模組需要讀取或更新它們,該模組就需要對外提供公開函式。回傳欄位值的函式,慣例上稱為 _getter_,更新欄位值的函式則稱為 _setter_。

getter 通常接受一個對 struct 的[參考 (reference)](./references),並回傳欄位值:

```move file=packages/samples/sources/move-basics/struct.move anchor=getter

```

setter 則接受一個對 struct 的可變參考,以及新的值:

```move file=packages/samples/sources/move-basics/struct.move anchor=setter

```

這兩個函式都可以用 `.` 運算子呼叫,就跟欄位存取一樣:

```move file=packages/samples/sources/move-basics/struct.move anchor=getter_setter_use

```

由於這些函式是 `public` 的,任何匯入 `Artist` 的模組都可以呼叫它們。請注意括號:`artist.name()` 是函式呼叫,在該函式可見的地方都能使用,而欄位存取 `artist.name` 在定義模組之外則無法編譯通過。

> `public fun` 語法定義了一個公開函式;函式在[函式 (Functions)](./function)一節中詳細說明。簽章中的 `&` 和 `&mut` 是參考——它們讓函式能夠讀取或修改一個值,而不需要取得其所有權。我們在[參考 (References)](./references)一節中說明它們,並在[結構體方法 (Struct Methods)](./struct-methods)一節中說明點呼叫語法。

雖然 getter 非常常見,但 setter 較少被定義,而且通常會附加額外的檢查。要對外暴露哪些函式,正是定義該型別介面的關鍵——模組決定外部程式碼能對其 struct 做什麼、不能做什麼。

## 拆解結構體 (Unpacking a Struct) {#unpacking-a-struct}

Struct 預設是不可丟棄的:一個 struct 值不能在函式結尾單純被留下不管——這樣做的程式碼無法編譯通過。每個建立的值都必須被使用:無論是儲存起來(例如放進另一個 struct,或如[使用物件 (Using Objects)](./../storage/)章節所示,保存在鏈上儲存中),或是被 _拆解 (unpacked)_。拆解 struct 意指將其解構為各個欄位,是打包的鏡像操作:使用 `let` 關鍵字,後面接 struct 名稱以及要綁定的欄位名稱。

```move file=packages/samples/sources/move-basics/struct.move anchor=unpack

```

在上面的範例中,我們拆解了 `Artist` struct,並建立一個新變數 `name`,其值為 `name` 欄位的值。在這一行之後,該 struct 值已不復存在——它已被拆解成各個部分。

如果不需要某個欄位,可以將它綁定到底線 `_` 來忽略。然而,由於 struct 本身不能被丟棄,其所有欄位仍必須在模式中列出:

```move file=packages/samples/sources/move-basics/struct.move anchor=unpack_ignore

```

對於欄位很多的 struct,逐一列出每個要忽略的欄位會很冗長。`..` 模式——_剩餘 (rest)_ 模式——可以一次比對所有剩餘的欄位:

```move file=packages/samples/sources/move-basics/struct.move anchor=unpack_rest

```

在上面的範例中,我們打包一個完整的 `Record`——`option::none()` 呼叫建立一個空的 `Option` 值,參見[Option](./option)一節——然後將其拆解,保留 `title` 和 `artist` 欄位,並用 `..` 忽略其餘欄位。

請注意,忽略一個欄位——無論用 `_` 或 `..`——會丟棄其值,而這只對可以被丟棄的值合法。像 `String`、`u16` 和 `bool` 這樣的簡單值可以自由丟棄,但 `Artist` 不行——這就是為什麼範例中同樣拆解出 `artist` 綁定,而不是直接忽略它。哪些值可以被丟棄、哪些不能,是由 _abilities_(能力)決定的,將在下面幾節說明——[能力介紹 (Abilities Introduction)](./abilities-introduction)和[能力:丟棄 (Ability: Drop)](./drop-ability)。

## 位置式結構體 (Positional Structs) {#positional-structs}

到目前為止,本頁的每個 struct 都有具名欄位。Move 也支援 _位置式 (positional)_ struct,其欄位沒有名稱,而是以位置來識別。位置式 struct 用括號而非曲括號定義,且該定義沒有主體——欄位列表結束後定義就結束了:

```move file=packages/samples/sources/move-basics/struct.move anchor=positional_def

```

abilities 在這裡也可以放在欄位之前或之後;在後置形式中,它們接在括號之後:`public struct Duration(u64, u64) has copy, drop;`。

位置式 struct 同樣以括號來打包和拆解,其欄位以 `.` 運算子加上欄位索引(從零開始)來存取:

```move file=packages/samples/sources/move-basics/struct.move anchor=positional_use

```

當欄位名稱不會為型別名稱本身已經傳達的資訊增加任何價值時,位置式 struct 是很好的選擇——通常用在只有一兩個欄位的小型包裝型別上。本頁所述的所有規則對它們同樣適用:欄位只能在定義模組內存取,且值必須被使用——儲存或拆解。對於欄位較多的 struct,具名欄位通常是較好的選擇。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考手冊中的[結構體 (Structs)](./../../reference/structs)。
