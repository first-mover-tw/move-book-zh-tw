---
description:
  'The Option type in Move: 表示可能不存在的值 (represent a value that may be absent)、建立與檢查選項
  (create and inspect options)、安全地取出值 (extract values safely)，並使用選項巨集 (option macros)
  處理它們。'
---

# 選項 (Option) {#option}

有些資料本質上就是選擇性的：使用者可能有、也可能沒有中間名，一次查找可能找到、也可能找不到相符結果。Move 沒有 `null` 或 `undefined` 值——`String` 型別的變數永遠持有一個字串——所以「值不存在」必須用其他方式表達。

第一直覺可能是保留一個特殊值當標記：用空字串代表缺少中間名，用零代表缺少數字。這種做法可行——直到空字串變成合法輸入，而每個函式都得記住哪些值是「真實的」、哪些只是佔位符。標準函式庫提供了更好的工具：`Option` 型別，這是 Move 從 Rust 借來的概念。

## Option 型別 (The Option Type) {#the-option-type}

`Option<Element>` 是對 `Element` 型別值的包裝，它永遠處於兩種狀態之一，慣例上稱為 `Some` 和 `None`：

- `Some` - option 包含一個值；
- `None` - option 是空的。

option 不會與它包裝的值混淆：`Option<String>` 不是 `String`，而且必須先檢查值是否存在並取出，才能使用它。「可能不存在」這件事本身成為型別的一部分，在每個函式簽名中都清楚可見，而不是每個呼叫端都必須記住的一項約定。

`Option` 定義於[標準函式庫 (Standard Library)](./standard-library)，和 `vector` 一樣是[隱式匯入 (implicit imports)](./standard-library#implicit-imports)——不需要 `use` 陳述式就能在任何模組中使用。`Element` 型別參數讓它成為[泛型 (generic)](./generics)：同一份定義可以服務 `Option<u64>`、`Option<String>` 以及任何其他元素型別。

以下是前面問題中的使用者記錄，其中選擇性欄位以 `Option<String>` 表示：

```move file=packages/samples/sources/move-basics/option.move anchor=registry

```

`middle_name` 欄位的型別正是特殊值做法無法表達的：值可能不存在，而且沒有任何 `String`——無論空字串或其他——被拿來當標記。這兩種情況分別用 `option::some(value)` 和 `option::none()` 建構：

```move file=packages/samples/sources/move-basics/option.move anchor=registry_use

```

## 建立與使用 Option (Creating and Using an Option) {#creating-and-using-an-option}

建立之後，option 可以檢查是否有值、讀取，以及清空：

```move file=packages/samples/sources/move-basics/option.move anchor=usage

```

> `borrow` 函式回傳指向該值的_參考 (reference)_——一種不需將值取出 option 就能讀取的方式。參考將在本章稍後的[參考 (References)](./references#immutable-references)小節中介紹。

下表列出 `std::option` 模組中最常用的函式；完整清單請參閱[模組文件][option-stdlib]：

<div class="modules-table">

| 函式                   | 說明                                | 何時中止 (Aborts If) |
| ---------------------- | ----------------------------------- | -------------------- |
| `is_some`              | 若 option 持有值則回傳 `true`       | -                    |
| `is_none`              | 若 option 為空則回傳 `true`         | -                    |
| `contains`             | 若 option 持有指定的值則回傳 `true` | -                    |
| `borrow`               | 回傳指向值的參考                    | option 為空          |
| `borrow_mut`           | 回傳指向值的可變參考                | option 為空          |
| `fill`                 | 將值放入空的 option                 | option 已持有值      |
| `extract`              | 取出值，使 option 變為空            | option 為空          |
| `swap`                 | 替換值，回傳舊值                    | option 為空          |
| `destroy_some`         | 銷毀 option，回傳其值               | option 為空          |
| `destroy_none`         | 銷毀空的 option                     | option 持有值        |
| `destroy_with_default` | 銷毀 option，回傳其值或預設值       | -                    |

</div>

和 `vector` 一樣，`Option` 的能力繼承自元素型別：非[可丟棄 (droppable)](./drop-ability)型別的 option 不能被忽略，必須用上述 `destroy_*` 函式之一明確銷毀。

## Option 巨集 (Option Macros) {#option-macros}

和[向量巨集 (vector macros)](./vector#vector-macros)一樣，option 巨集用單一運算式取代常見的「先檢查再取出」序列：

```move file=packages/samples/sources/move-basics/option.move anchor=macros

```

其他常用的巨集包括 `map!`、`filter!`、`extract_or!` 和 `do_ref!`——完整清單可在[模組文件][option-stdlib]中找到，巨集的一般性介紹則在本章稍後的[巨集函式 (Macro Functions)](./macros)小節。

## 底層原理 (Under the Hood) {#under-the-hood}

`Option` 定義為只有一個欄位的結構：一個 `Element` 的 `vector`，該 vector 永遠不是空的（`None`）就是恰好持有一個值（`Some`）：

```move
module std::option;

/// 表示可能存在也可能不存在的值的抽象。
public struct Option<Element> has copy, drop, store {
    vec: vector<Element>
}
```

> 你可能會驚訝 `Option` 是一個包含 `vector` 的結構，而不是一個 [enum][enum-reference]。這是歷史因素造成的：`Option` 在 Move 語言支援 enum 之前就已經加入了。在 Rust（這個型別的發源地）中，`Option` _就是_一個帶有 `Some` 和 `None` _變體 (variants)_ 的 enum——Move 沿用了這套術語。

這種內部表示方式屬於實作細節：上述函式與巨集已涵蓋一般用途，`vec` 欄位不會被直接存取。

## 延伸閱讀 (Further Reading) {#further-reading}

- [std::option][option-stdlib] 模組文件。

[enum-reference]: ./../../reference/enums
[option-stdlib]: https://docs.sui.io/references/framework/std/option
