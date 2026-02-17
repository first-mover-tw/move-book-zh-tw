---

description: "References in Move: immutable and mutable borrows, the borrow checker, and how to safely pass values without transferring ownership."
---

# 參照 (References)

<!--

Chapter: Basic Syntax
Goal: Show what the borrow checker is and how it works.
Notes:
    - give the metro pass example
    - show why passing by reference is useful
    - mention that reference comparison is faster
    - references can be both mutable and immutable
    - immutable access to shared objects is faster
    - implicit copy
    - moving the value
    - unpacking a reference (mutable and immutable)

 -->

在 [所有權與作用域](./ownership-and-scope) 章節中，我們解釋了當一個值傳遞給函式時，它會被 **移動 (moved)** 到該函式的作用域中。這意味著該函式成為了該值的所有者，而原始作用域（原所有者）將無法再使用它。這是 Move 中的一個重要概念，因為它確保了值不會同時在多個地方被使用。然而，在某些使用案例中，我們希望將值傳遞給函式但保留其所有權。這就是 **參照 (References)** 發揮作用的地方。

為了說明這一點，讓我們考慮一個簡單的範例 — 地鐵乘車卡應用程式。我們將查看卡片的 4 種不同情境：

1. 在自助服務機以固定價格購買
2. 向查票員出示以證明乘客持有有效卡片
3. 在閘門處使用以進入地鐵並支付一段車資
4. 卡片餘額用盡後進行回收

## 版面佈局 (Layout)

地鐵卡應用程式的初始佈局很簡單。我們定義了 `Card` 類型和一個表示單張卡片乘車次數的 `USES` [常數](./constants)。我們也為卡片餘額充足與否的情況添加了 [錯誤常數](./assert-and-abort#error-constants)。

```move file=packages/samples/sources/move-basics/references.move anchor=header_new
module book::metro_pass;


```

<!-- In [the previous section](./ownership-and-scope) we explained the ownership and scope in Move. We showed how the value is *moved* to a new scope, and how it changes the owner. In this section, we will explain how to *borrow* a reference to a value to avoid moving it, and how Move's *borrow checker* ensures that the references are used correctly. -->

## 參照 (References)

參照是一種在不放棄所有權的情況下，向函式 **展示** 一個值的方法。在我們的案例中，當我們向查票員出示卡片時，我們並不希望放棄它的所有權，也不允許查票員消耗我們的乘車次數。我們只是想允許 **讀取** 卡片的值並證明其所有權。

為此，在函式簽名中，我們使用 `&` 符號來表示我們傳遞的是該值的 **參照**，而非值本身。

```move file=packages/samples/sources/move-basics/references.move anchor=immutable

```

由於該函式並不取得卡片的所有權，它可以 **讀取** 其資料但不能 **寫入**，這意味著它不能修改乘車次數。此外，函式簽名確保了在沒有卡片實例的情況下無法呼叫它。這是一個重要的屬性，使得 [能力模式 (Capability Pattern)](./../programmability/capability) 成為可能，我們將網在接下來的章節中介紹。

建立值的參照通常被稱為「借用 (borrowing)」該值。例如，獲取封裝在 `Option` 中的值的參照的方法就稱為 `borrow`。

## 可變參照 (Mutable Reference)

在某些情況下，我們希望允許函式修改卡片。例如，在閘門處使用卡片時，我們需要扣除一次乘車次數。為了實現這一點，我們在函式簽名中使用 `&mut` 關鍵字。

```move file=packages/samples/sources/move-basics/references.move anchor=mutable

```

正如您在函式主體中看到的，`&mut` 參照允許修改該值，使函式可以消耗乘車次數。

## 按值傳遞 (Passing by Value)

最後，讓我們說明當我們將值本身傳遞給函式時會發生什麼。在這種情況下，函式取得該值的所有權，使其在原始作用域中無法再被存取。卡片的所有者可以回收它，從而將所有權轉移給函式。

```move file=packages/samples/sources/move-basics/references.move anchor=move

```

在 `recycle` 函式中，卡片按值傳遞，所有權轉移到該函式。這使得卡片可以被解構並銷毀。

> 注意：在 Move 中，`_` 是解構中使用的萬用字元模式，用於忽略某個欄位，但同時仍會消耗該值。解構必須匹配結構類型中的所有欄位。如果結構具有欄位，您必須明確列出所有欄位，或使用 `_` 來忽略不需要的欄位。

## 完整範例

為了說明應用程式的完整流程，讓我們在測試中將所有部分組合在一起。

```move file=packages/samples/sources/move-basics/references.move anchor=move_2024

```

## 延伸閱讀

- Move 參考手冊中的 [參照 (References)](/reference/primitive-types/references)。

<!-- ## Dereference and Copy -->

<!-- TODO: defer and copy, *& -->

<!-- ## Notes -->

<!--
    Move 2024 is great but it's better to show the example with explicit &t and &mut t
    ...and then say that the example could be rewritten with the new syntax


-->

<!-- ## Move 2024

Here's the test from this page written with the Move 2024 syntax:

```move file=packages/samples/sources/move-basics/references.move anchor=move_2024
```
-->
