---

description: "The Option type in Move: represent optional values safely, with methods for creating, checking, extracting, and destroying options."
---

# 選項 (Option)

`Option` 是一種表示「可能存在也可能不存在」的可選值的類型。Move 中 `Option` 的概念借鑒自 Rust，它是 Move 中非常實用的原始類型。`Option` 定義在 [標準庫](./standard-library) 中，定義如下：

```move
module std::option;

/// 對可能存在也可能不存在的值的抽象。
public struct Option<Element> has copy, drop, store {
    vec: vector<Element>
}
```

_參閱 [std::option 模組完整文件][option-stdlib]。_

> `std::option` 模組在每個模組中都會被隱式匯入，因此您不需要添加明確的匯入語句。

`Option` 類型是一個具有 `Element` 類型參數的泛型類型。它包含一個名為 `vec` 的欄位，這是一個 `Element` 的 `vector`（向量）。該向量的長度可以為 0 或 1，分別代表值的缺失或存在。

> 注意：您可能會對 `Option` 是一個包含 `vector` 的 `struct` 而不是 [列舉 (enum)][enum-reference] 感到驚訝。這是由於歷史原因：`Option` 在 Move 支援列舉之前就被添加進去了。

`Option` 類型有兩個變體：`Some` 和 `None`。`Some` 變體包含一個值，而 `None` 變體表示值的缺失。`Option` 類型用於以類型安全的方式表示值的缺失，從而避免對空值或 `undefined` 值的需求。

## 實務應用

為了展示為何需要 `Option` 類型，讓我們看一個範例。假設一個應用程式接收使用者輸入並將其儲存在變數中。有些欄位是必填的，有些是選填的。例如，使用者的中間名 (middle name) 是選填的。雖然我們可以使用空字串來表示中間名的缺失，但這需要額外的檢查來區分空字串和確實缺失的中間名。相反，我們可以使用 `Option` 類型來表示中間名。

```move file=packages/samples/sources/move-basics/option.move anchor=registry

```

在前面的範例中，`middle_name` 欄位的類型為 `Option<String>`。這意味著 `middle_name` 欄位既可以包含封裝在 Some 中的 String 值，也可以是明確為空的（由 None 表示）。使用 `Option` 類型使該欄位的可選性質變得明確，避免了歧義，也不需要額外的檢查來區分空字串和缺失的中間名。

## 建立與使用 Option 值

`Option` 類型以及 `std::option` 模組在 Move 中是隱式匯入的。這意味著您可以直接使用 `Option` 類型，而不需要 `use` 語句。

要建立 `Option` 類型的值，您可以使用 `option::some` 或 `option::none` 方法。`Option` 值也支援多種操作（借用將在 [參照 (references)](references#references-1) 章節中討論）：

```move file=packages/samples/sources/move-basics/option.move anchor=usage

```

## 延伸閱讀

- 標準庫中的 [std::option][option-stdlib]

[enum-reference]: ./../../reference/enums
[option-stdlib]: https://docs.sui.io/references/framework/std/option
