---
description: 所有權與作用域 (Ownership and Scope)：在 Move 中，值如何在作用域間被移動、為何無法被複製或遺失，以及編譯器如何強制執行此規則。
---

# 所有權與範圍 (Ownership and Scope) {#ownership-and-scope}

Ownership 是 Move 的核心概念——事實上，這門語言的名字就是由此而來。Move 是為數位資產而設計的，它的主要承諾是：一個值不能被複製，也不會意外遺失。實現這個承諾的機制就是所有權（ownership），並由編譯器強制執行：違反規則的程式無法通過編譯。

規則如下：

- 每個值恰好有一個擁有者——即定義它的作用域。
- 當一個值被傳遞給函式、指派給新變數，或被回傳時，它會被*移動*（moved）到新的擁有者，而先前的擁有者將無法再使用它。
- 當一個作用域結束時，它仍擁有的每個值都必須是可捨棄的，或已經被移出。

本節接下來會逐一講解這些規則。如果其中有些看起來很嚴格——這正是重點：這些限制正是讓 Move 能安全地把值當作資產處理的原因。

## 變數作用域 (Variable Scope) {#variable-scope}

作用域（scope）是一個值有效的程式碼範圍。在函式中定義的變數，由該函式的作用域所擁有：它在宣告時進入作用域，並在函式結束時離開作用域。

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=scope

```

到目前為止都沒有什麼令人意外的——大多數語言中的區域變數就是這樣運作的。當一個值需要離開其作用域時，所有權才變得有趣。

## 移動一個值 (Moving a Value) {#moving-a-value}

為了示範這些規則，我們會使用一個小模組，裡面有一個 `Coin` 型別和兩個函式——一個用來建立硬幣，另一個用來銷毀它：

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=coin

```

`Coin` 結構體沒有[能力](./abilities-introduction)，因此編譯器對其值施加了最嚴格的限制：它們既不能被複製，也不能被捨棄。像這樣的值只能易主——這正是我們希望資產具備的特性。

當一個值被傳遞給函式時，它會被*移動*進該函式的作用域。函式成為新的擁有者，而呼叫者則失去對該值的存取權。這稱為*移動語意*（move semantics）。

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=move_to_function

```

讓我們看看如果違反這條規則，在 `coin` 被移動之後仍嘗試使用它會發生什麼事：

```move
#[test]
fun test_move_semantics() {
    let coin = mint(100);
    spend(coin); // 該值的所有權移動進入 `spend`
    spend(coin); // 錯誤！`coin` 已經被移動了
}
```

上面的程式碼不會通過編譯，編譯器會精確指出該值被移動的位置：

```text
error[E06002]: use of unassigned variable
   ┌─ sources/ownership.move:12:11
   │
11 │     spend(coin);
   │           ----
   │           │
   │           The value of 'coin' was previously moved here.
   │           Suggestion: use 'copy coin' to avoid the move.
12 │     spend(coin);
   │           ^^^^ Invalid usage of previously moved variable 'coin'.
```

編譯器建議使用 `copy coin`，但這只對可複製的值有效——而 `Coin` 並不是。同一枚硬幣沒有辦法花費兩次，而這項保證在程式碼執行之前就已經被檢查過了。

將一個值指派給新變數同樣也是一種移動。值本身沒有改變或被複製——改變的只有它的擁有者：

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=move_to_variable

```

## 回傳一個值 (Returning a Value) {#returning-a-value}

移動也可以朝相反方向運作：函式可以回傳一個值，將其移動到呼叫者的作用域。這就是範例中的 `mint` 函式如何將新建立的硬幣所有權轉移給呼叫者的方式。結合值傳遞，這完整呈現了一個值的生命週期：`mint` 建立硬幣並交給測試函式，測試函式再將其交給 `spend`，最終將其銷毀。在程式的每一個時間點，這枚硬幣都恰好只有一個擁有者。

## 每個值都必須被使用 (Every Value Must Be Used) {#every-value-must-be-used}

如果一個值從未被傳遞出去會怎樣呢？讓我們建立一枚硬幣，然後直接讓函式結束：

```move
#[test]
fun test_lose_a_coin() {
    let coin = mint(100);
} // 錯誤！`coin` 仍然包含一個無法被捨棄的值
```

第三條規則開始發揮作用：作用域不能在仍擁有一個不可捨棄值的情況下結束。

```text
error[E06001]: unused value without 'drop'
  ┌─ sources/ownership.move:7:35
  │
4 │ public struct Coin { value: u64 }
  │               ---- To satisfy the constraint, the 'drop' ability would need to be added here
  ·
7 │     let coin = mint(100);
  │         ----  ↑ The local variable 'coin' still contains a value.
  │                The value does not have the 'drop' ability and must
  │                be consumed before the function returns
```

一個值是否可以被捨棄，是由 `drop` 能力控制的，我們在[能力：Drop](./drop-ability)一節中已經介紹過。對於像 `Coin` 這樣的型別，沒有 `drop` 意味著硬幣不能被遺忘在區域變數中而悄悄消失——持有它的程式碼被強制必須對它做些什麼。

## 可複製型別 (Copyable Types) {#copyable-types}

有些值不需要這種程度的保護。所有原始型別——整數、`bool`、`address`——都具有 `copy` 能力，在被指派或傳遞給函式時，它們不是被移動，而是被複製：

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=copy_types

```

原始型別的複製是隱式的，因為它們體積小、複製成本低。自訂型別也可以透過新增 `copy` 能力來選擇加入這種行為，我們會在[能力：Copy](./copy-ability)一節中介紹。

如果需要，一個可複製的值仍然可以使用 `move` 關鍵字被明確移動：

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=explicit_move

```

## 作用域與程式碼區塊 (Scopes and Blocks) {#scopes-and-blocks}

除了函式的主要作用域之外，每個程式碼區塊（block）也會形成自己的作用域。在區塊內宣告的變數由該區塊所擁有，並在區塊結束時離開作用域。區塊內的程式碼可以存取外層作用域的變數，但反過來則不行：

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=blocks

```

區塊是一種運算式，其結果值會被移動到外層作用域——與從函式回傳值相同的移動語意：

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=block_return

```

## 下一步 (Next Steps) {#next-steps}

到目前為止，讓函式使用某個值的唯一方式就是交出所有權。如果每個操作都這樣做將會很不切實際——讀取一個欄位不應該需要交出整個值。Move 透過*參考*（references）解決了這個問題，它允許函式借用一個值而不取得所有權。我們會在[參考](./references)一節中介紹它們。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考手冊中的[區域變數與作用域](./../../reference/variables)
