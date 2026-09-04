---
description: Move 中的所有權與範圍：值如何在範圍之間轉移、為何無法複製或遺失，以及編譯器如何強制執行。
title: 所有權 (Ownership) 與範圍 (Scope)
keywords:
  - Move
  - Sui
  - Move tutorial
  - ownership
  - scope
questions:
  - What is Ownership and Scope in Move?
  - How do I use Ownership and Scope in Move?
  - What is Variable Scope in Move?
  - What is Moving a Value in Move?
answer: 'Ownership and scope in Move: how values are moved between scopes, why they cannot be copied or lost, and how the compiler enforces it.'
goal:
  description: 'Reader understands ownership and scope in Move: how values are moved between scopes, why they cannot be copied or lost, and how the compiler enforces it'
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

# 所有權與作用域 (Ownership and Scope) {#ownership-and-scope}

所有權是 Move 的核心概念——這甚至是此語言名稱的由來。Move 專為數位資產設計，其主要承諾是：一個值無法被複製，也不會意外遺失。此承諾背後的機制是所有權，並由編譯器強制執行：違反規則的程式無法編譯。

規則如下：

- 每個值都恰有一個擁有者——也就是定義它的作用域。
- 當值被傳遞給函式、指派給新的變數或回傳時，它會被*移動*至新的擁有者，先前的擁有者便無法再使用它。
- 當作用域結束時，它仍擁有的每個值都必須可丟棄，或已經被移出。

本節其餘內容會逐一說明這些規則。若其中一些規則看似嚴格——這正是目的所在：這些限制讓你能安全地將 Move 中的值視為資產。

## 變數作用域 (Variable Scope) {#variable-scope}

作用域是值有效的程式碼範圍。在函式中定義的變數由該函式的作用域擁有：它在宣告時進入作用域，並在函式結束時離開作用域。

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=scope

```

目前沒有令人意外之處——這也是大多數語言中區域變數的行為方式。當值需要離開其作用域時，所有權才會變得有意思。

## 移動值 (Moving a Value) {#moving-a-value}

為了示範這些規則，我們會使用一個小型模組，其中包含 `Coin` 型別與兩個函式——一個用於建立硬幣，另一個用於銷毀硬幣：

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=coin

```

`Coin` 結構沒有任何[能力](./abilities-introduction)，因此編譯器會對其值施加最嚴格的限制：它們無法複製，也無法丟棄。這類值只能轉手——這正是我們對資產的期待。

當值被傳遞給函式時，它會被*移動*到函式的作用域中。函式成為新的擁有者，而呼叫端會失去對該值的存取權。這稱為*移動語意*。

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=move_to_function

```

讓我們看看違反規則並嘗試在 `coin` 被移動後使用它時會發生什麼事：

```move
#[test]
fun test_move_semantics() {
    let coin = mint(100);
    spend(coin); // 值的所有權移動至 `spend`
    spend(coin); // 錯誤！`coin` 已經被移動
}
```

上述程式碼無法編譯，編譯器會指出值被移動的確切位置：

```text
error[E06002]: 使用未指派的變數
   ┌─ sources/ownership.move:12:11
   │
11 │     spend(coin);
   │           ----
   │           │
   │           值 'coin' 先前已在此處被移動。
   │           建議：使用 'copy coin' 以避免移動。
12 │     spend(coin);
   │           ^^^^ 無效地使用先前已移動的變數 'coin'。
```

編譯器建議使用 `copy coin`，但這僅適用於可複製的值——而 `Coin` 並非如此。你無法花費同一枚硬幣兩次，且此保證會在程式碼執行前檢查。

將值指派給新的變數也是一次移動。值本身不會改變或被複製——只有它的擁有者改變：

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=move_to_variable

```

## 回傳值 (Returning a Value) {#returning-a-value}

移動也能往相反方向運作：函式可以回傳一個值，將其移動到呼叫端的作用域。這就是範例中的 `mint` 函式如何將新建立硬幣的所有權轉移給呼叫它的人。搭配依值傳遞，這完整呈現了值的生命週期：`mint` 建立硬幣並交給測試函式，測試函式接著將其交給 `spend`，後者將它銷毀。在程式中的每個時間點，硬幣都恰有一個擁有者。

## 每個值都必須被使用 (Every Value Must Be Used) {#every-value-must-be-used}

若值從未被傳遞出去會如何？讓我們鑄造一枚硬幣，然後直接讓函式結束：

```move
#[test]
fun test_lose_a_coin() {
    let coin = mint(100);
} // 錯誤！`coin` 仍包含無法丟棄的值
```

第三項規則開始生效：作用域不能在仍擁有不可丟棄值的情況下結束。

```text
error[E06001]: 沒有 'drop' 的未使用值
  ┌─ sources/ownership.move:7:35
  │
4 │ public struct Coin { value: u64 }
  │               ---- 若要滿足此限制，必須在此處加入 'drop' 能力
  ·
7 │     let coin = mint(100);
  │         ----  ↑ 區域變數 'coin' 仍包含一個值。
  │                該值沒有 'drop' 能力，且必須
  │                在函式回傳前被消耗
```

值是否可被丟棄由 `drop` 能力控制，這已在[能力：Drop](./drop-ability)章節中介紹。對於像 `Coin` 這樣的型別，缺少 `drop` 代表硬幣無法被遺忘在區域變數中並悄然消失——持有它的程式碼必須對它進行某種處理。

## 可複製型別 (Copyable Types) {#copyable-types}

有些值不需要這種程度的保護。所有原始型別——整數、`bool`、`address`——皆具備 `copy` 能力，在被指派或傳遞給函式時會被複製，而非移動：

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=copy_types

```

原始型別會隱含地複製，因為它們很小且複製成本低。自訂型別也可透過加入 `copy` 能力來選擇此行為，這會在[能力：Copy](./copy-ability)章節中介紹。

若有需要，仍可使用 `move` 關鍵字明確移動可複製的值：

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=explicit_move

```

## 作用域與區塊 (Scopes and Blocks) {#scopes-and-blocks}

除了函式的主要作用域外，每個區塊也會形成自己的作用域。在區塊內宣告的變數由該區塊擁有，並在區塊結束時離開作用域。區塊內的程式碼可存取外層作用域的變數，但反之則不行：

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=blocks

```

區塊是一個運算式，其結果值會被移動到外層作用域——與從函式回傳值時相同的移動語意：

```move file=packages/samples/sources/move-basics/ownership-and-scope.move anchor=block_return

```

## 後續步驟 (Next Steps) {#next-steps}

到目前為止，讓函式使用值的唯一方式是交出所有權。若每項操作都如此，將不切實際——讀取欄位不應要求交出整個值。Move 透過*參考*解決此問題，讓函式能借用值而不取得所有權。我們會在[參考](./references)章節中介紹它們。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[區域變數與作用域](./../../reference/variables)。
