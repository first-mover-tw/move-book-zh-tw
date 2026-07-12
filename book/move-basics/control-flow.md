---
description: 控制流程 (Control Flow)：Move 中的 if/else 運算式、while 與 loop 結構、break、continue
  與 return 陳述式。
---

# 控制流程 (Control Flow) {#control-flow}

控制流程陳述式決定哪些程式碼會執行、執行幾次，以及何時停止。它們用來
做決策、重複執行一個程式碼區塊，或提早跳出一個程式碼區塊。Move 包含以下
控制流程陳述式（詳細說明如下）：

- [`if` 與 `if-else`](#conditional-statements) - 決定是否執行一個程式碼
  區塊
- [`loop` 與 `while` 迴圈](#repeating-statements-with-loops) - 重複執行一個程式碼區塊
- [`break` 與 `continue` 陳述式](#exiting-a-loop-early) - 提早跳出迴圈
- [標籤化控制流程 (labeled control flow)](#labeled-control-flow) - 從巢狀迴圈或區塊中鎖定外層迴圈或區塊
- [`return`](#early-return) 陳述式 - 提早結束函式

## 條件陳述式 (Conditional Statements) {#conditional-statements}

`if` 運算式用於在程式中做出決策。它會評估一個
[布林值](./primitive-types#booleans)運算式，並在運算式為真時執行一段程式碼區塊。
搭配 `else`，它可以在運算式為假時執行另一段程式碼區塊。

`if` 運算式的語法為：

```move
if (<bool_expression>) <expression>;
if (<bool_expression>) <expression> else <expression>;
```

就像任何其他運算式一樣，如果後面還有其他運算式，`if` 就需要分號。`else`
關鍵字是可選的，除非結果值被賦值給一個變數，因為所有分支都必須回傳一個值以確保型別安全。讓我們透過以下範例來檢視
`if` 運算式在 Move 中是如何運作的：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=if_condition

```

讓我們看看如何使用 `if` 和 `else` 將值賦值給一個變數：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=if_else

```

在這個範例中，`if` 運算式的值被賦值給變數 `y`。如果 `x` 大於
0，`y` 會被賦值為 1；否則，它會被賦值為 0。這裡需要 `else` 區塊，
因為 `if` 運算式的兩個分支都必須具有相同的型別。當省略 `else` 時，假分支預設為單元值
`()`，因此將沒有 `else` 的 `if` 賦值給變數會是型別錯誤：

```move
let y = if (x > 0) 1;
//      ^^^^^^^^^^^^ 錯誤！預期是 `u64`，但找到 `()` - 缺少的
//                   else 分支預設為 unit 值 `()`。
```

要在兩個以上的分支之間做選擇，`if` 運算式可以用 `else if` 串連起來。這些
分支由上到下逐一檢查，並採用第一個條件為真的分支：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=else_if

```

條件運算式是 Move 中最重要的控制流程陳述式之一。它們評估
使用者提供的輸入或已儲存的資料以做出決策。一個關鍵的使用案例是在
[`assert!` 巨集](./assert-and-abort)中，它會檢查一個條件是否為真，若不為真則中止執行。
我們會在本章稍後詳細探討它。

## 以迴圈重複執行陳述式 (Repeating Statements with Loops) {#repeating-statements-with-loops}

迴圈用於多次執行一段程式碼區塊。Move 有兩種內建的迴圈型別：
`loop` 和 `while`。多數情況下兩者可以互換使用，但通常 `while` 用於事先已知
迭代次數的情況，而 `loop` 用於事先不知道迭代次數或有多個退出點的情況。

迴圈適用於處理集合（例如向量），或是重複執行一段程式碼直到滿足特定條件為止。
然而，請留意避免無窮迴圈，因為這會耗盡 gas 上限並導致交易中止。

> 實務上，手寫迴圈在 Move 中相對少見。走訪集合更常以較高階的
> [巨集 (macros)](./macros) 來表達，例如 `do!`、`map!` 和 `fold!`，
> 這些會在 [Vector](./vector#vector-macros) 章節中介紹。這裡描述的 `loop` 和 `while`
> 結構是這些巨集的建構基礎，當迭代不符合單純的集合走訪情境時，
> 它們仍是正確的工具。

## while 迴圈 (The `while` Loop) {#the-while-loop}

只要對應的布林運算式求值為 true，`while` 陳述式就會重複執行一段程式碼區塊。就像我們在 `if` 中看到的一樣，布林運算式會在迴圈的每次疊代之前被求值。此外，和條件陳述式一樣，`while` 迴圈是一個運算式，如果後面還有其他運算式，就需要分號。

`while` 迴圈的語法為：

```move
while (<bool_expression>) { <expressions>; };
```

以下是一個條件非常簡單的 `while` 迴圈範例：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=while_loop

```

## 無窮 `loop` (Infinite `loop`) {#infinite-loop}

現在讓我們設想一種情境：布林運算式永遠為 `true`。例如，如果我們直接把 `true` 傳給
`while` 的條件。這類似 `loop` 陳述式的運作方式，差別在於 `while` 會評估一個條件。

```move file=packages/samples/sources/move-basics/control-flow.move anchor=infinite_while

```

一個無窮的 `while` 迴圈,或者說一個條件永遠為 `true` 的 `while` 迴圈,等同於一個
`loop`。建立 `loop` 的語法很直接:

```move
loop { <expressions>; };
```

讓我們把先前的範例改用 `loop` 而非 `while` 重寫:

```move file=packages/samples/sources/move-basics/control-flow.move anchor=infinite_loop

```

無窮迴圈在 Move 中很少實用,因為每個操作都會消耗 gas,無窮迴圈勢必會導致 gas 耗盡。
如果你發現自己在使用迴圈,不妨思考是否有更好的做法,因為許多使用情境用其他控制
流程結構處理會更有效率。話雖如此,`loop` 搭配 `break` 和 `continue` 陳述式使用時,
或許能發揮作用,創造出可控且靈活的迴圈行為。

## 提前跳出迴圈 (Exiting a Loop Early) {#exiting-a-loop-early}

正如我們之前提過的，無窮迴圈本身其實沒什麼用處。這時就要介紹 `break` 和 `continue` 陳述式了。它們分別用於提前跳出迴圈，以及跳過當前這輪迭代的剩餘部分。

`break` 陳述式的語法如下（不需要分號）：

```move
break
```

`break` 陳述式用於停止迴圈的執行並提前跳出。它經常與條件陳述式搭配使用，在符合特定條件時跳出迴圈。為了說明這一點，讓我們把前面範例中的無窮 `loop` 改寫成外觀和行為都更像 `while` 迴圈的樣子：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=break_loop

```

幾乎和 `while` 迴圈一模一樣，對吧？當 `x` 等於 5 時，`break` 陳述式會用來跳出迴圈。如果我們移除 `break` 陳述式，這個迴圈就會像前面的範例一樣永遠執行下去。

## 跳過一次迭代 (Skipping an Iteration) {#skipping-an-iteration}

`continue` 陳述式用於跳過目前迭代的剩餘部分，並開始下一次迭代。
與 `break` 類似，它通常搭配條件陳述式使用，在滿足特定條件時跳過該次
迭代的剩餘部分。

`continue` 陳述式的語法如下（不需加分號）：

```move
continue
```

以下範例會跳過奇數，只印出 0 到 10 之間的偶數：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=continue_loop

```

`break` 與 `continue` 陳述式可以同時用於 `while` 與 `loop` 迴圈中。

## 具名控制流程 (Labeled Control Flow) {#labeled-control-flow}

在預設情況下，`break` 和 `continue` 作用於包住它們的最內層迴圈。當迴圈是巢狀的時候，這會是個問題：從內層迴圈裡面，沒有辦法跳出外層迴圈。為了解決這個問題，Move 讓你可以為迴圈附加一個 _標籤 (label)_，然後告訴 `break` 或 `continue` 究竟要鎖定哪一個迴圈。

標籤是一個以單引號為前綴的名稱，放在 `loop` 或 `while` 關鍵字之前。接著你就可以寫 `break 'label` 或 `continue 'label`，跳到指定標籤的迴圈，而不是最內層的迴圈：

```move
'outer: loop {
    while (condition) {
        // 一次跳出兩層迴圈。
        break 'outer;

        // 跳到外層迴圈的下一次迭代。
        continue 'outer;
    };
};
```

想像一個對網格（grid）的搜尋——一個由列（row）組成的向量，而每一列本身也是一個向量。一旦我們找到要找的值，就想完全停止掃描，而不只是完成目前這一列。為外層迴圈加上標籤，可以讓內層的 `while` 迴圈一步就放棄整個搜尋：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=labeled_loop

```

注意 `break` 陳述式也帶有值：`break false` 和 `break 'search true`。`loop` 是一個運算式，所以跳出它可以產生一個結果——在這裡就是函式回傳的布林值。這是 `loop` 特有的：`while` 迴圈永遠會求值為單元值 `()`，所以它的 `break` 不能帶有值。如果沒有標籤，要跳出兩層迴圈就需要額外一個旗標變數，並在外層迴圈再做一次檢查。

### 具名區塊 (Labeled Blocks) {#labeled-blocks}

標籤不僅限於迴圈。一般的區塊 `{ ... }` 也可以加上標籤，然後用 `return 'label <value>` 提前結束它。這在計算一個有多個可能提前退出點的值時很有用，不需要把邏輯抽取成獨立的函式：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=labeled_block

```

在這裡，`'result` 區塊會產生一個值，而任何一個 `return 'result` 陳述式都可以提前結束它。這在搭配上面提到的走訪 [巨集 (macros)](./macros) 時特別強大，具名區塊可以讓 lambda 帶著結果跳出走訪。

有兩條規則值得牢記：

- 標籤只能放在 `loop`、`while` 或區塊 `{}` 上——**不能**放在 `if` 運算式上。要為條件式加上標籤，就為它外面的區塊加上標籤（`if` 的分支本身就是一個區塊）。
- `break` 和 `continue` 只能搭配 _迴圈_ 標籤使用，而 `return` 只能搭配 _區塊_ 標籤使用。混用它們（例如對區塊標籤使用 `break`）會導致編譯錯誤。

> Move 參考手冊的[具名控制流程 (Labeled Control Flow)](./../../reference/control-flow/labeled-control-flow) 章節更詳細地介紹了這些形式，包括它們與巨集的互動方式。

## 提前回傳 (Early Return) {#early-return}

`return` 陳述式用於提前退出[函式](./function)並回傳一個值。它通常與條件陳述式搭配使用，在滿足特定條件時提前退出函式。`return` 陳述式的語法為：

```move
return <expression>
```

以下是一個範例，展示函式在滿足特定條件時回傳一個值：

```move file=packages/samples/sources/move-basics/control-flow.move anchor=return_statement

```

與許多其他語言不同，函式中最後一個運算式並不需要使用 `return` 陳述式。函式區塊中的最後一個運算式會自動被回傳。然而，當我們想在滿足特定條件時提前退出函式，`return` 陳述式就非常有用。

## 進階閱讀 (Further Reading) {#further-reading}

- Move 參考手冊中的[控制流程](./../../reference/control-flow)章節。
