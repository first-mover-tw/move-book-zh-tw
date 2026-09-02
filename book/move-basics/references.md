---
description:
  'References in Move: immutable and mutable borrows, the borrow checker, and how to safely pass values without transferring ownership.


  翻譯：


  Move 中的參考 (References)：不可變借用與可變借用、借用檢查器 (borrow checker)，以及如何在不轉移所有權的情況下安全傳遞值。'
---

# 參考 (References) {#references}

在[所有權與範圍](./ownership-and-scope)章節中，我們解釋過當一個值被傳遞給函式時，它會被_移動_到該函式的範圍內。這代表函式會成為該值的擁有者，而原本的範圍（擁有者）將無法再使用它。這是 Move 中一個重要的概念，因為它確保了同一個值不會同時在多個地方被使用。然而，有些使用情境下我們希望將值傳遞給函式，但保留其所有權。這就是參考發揮作用的地方。

為了說明這一點，讓我們考慮一個簡單的範例——一個地鐵（捷運）通行卡的應用程式。我們將探討 4 種不同的情境，其中卡片可以：

1. 在售票機以固定價格購買
2. 出示給查票員以證明乘客持有有效的通行卡
3. 在閘門使用以進入地鐵，並購買一趟車程
4. 在用完後回收

## 地鐵通行卡應用程式 (The Metro Pass Application) {#the-metro-pass-application}

地鐵通行卡應用程式的初始架構很簡單。我們定義 `Card` 型別以及代表單張卡片可乘車次數的 `USES` [常數](./constants)。我們也加入[錯誤常數](./assert-and-abort#error-constants)，用於卡片已用盡以及卡片尚未用盡的情況。

```move file=packages/samples/sources/move-basics/references.move anchor=header_new
module book::metro_pass;


```

## 不可變參考 (Immutable References) {#immutable-references}

參考是一種在不放棄所有權的情況下，將值_展示_給函式的方法。在我們的範例中，當我們將卡片出示給查票員時，我們不希望放棄它的所有權，也不允許查票員使用掉我們的任何乘車次數。我們只想允許_讀取_卡片的值，並證明其所有權。

為此，在函式簽章中，我們使用 `&` 符號來表示我們傳遞的是值的一個_參考_，而非值本身。

```move file=packages/samples/sources/move-basics/references.move anchor=immutable

```

因為此函式沒有取得 Card 的所有權，它可以_讀取_其資料，但無法_寫入_它，也就是說它無法修改乘車次數。此外，函式簽章確保了它無法在沒有 Card 實例的情況下被呼叫。這是一個重要的特性，它使得我們將在後續章節介紹的[能力模式（Capability Pattern）](./../programmability/capability)得以實現。

`&` 運算子並不侷限於函式簽章：它是一個可以套用於任何值或結構體單一欄位的運算式。產生的參考可以儲存在區域變數中並傳遞下去：

```move
let card = purchase();

let card_ref = &card;       // 對整個值的參考
let uses_ref = &card.uses;  // 對單一欄位的參考
```

建立一個值的參考通常被稱為「借用」該值。舉例來說，取得 `Option` 所包裝值之參考的方法就叫做 `borrow`。

## 可變參考 (Mutable Reference) {#mutable-reference}

在某些情況下，我們希望允許函式修改 Card。舉例來說，當在閘門使用卡片時，我們需要扣除一次乘車次數。為了達成這一點，我們在函式簽章中使用 `&mut` 關鍵字。

```move file=packages/samples/sources/move-basics/references.move anchor=mutable

```

如你在函式主體中所見，`&mut` 參考允許修改值，函式因而能夠花費乘車次數。

可變參考可以在任何預期不可變參考的地方使用：將 `&mut card` 傳遞給 `is_valid` 函式完全沒問題，該函式只是不會修改這個值而已。反過來則不成立——不可變參考永遠無法轉換成可變參考。

## 借用檢查器 (The Borrow Checker) {#the-borrow-checker}

參考是在_借用檢查器_（borrow checker）的協助下編譯的——這是編譯器中負責追蹤每一次借用，並拒絕可能不安全地使用參考之程式的部分。它所強制執行的規則有：

- 當一個值被借用時，它不能被移動、依值傳遞或銷毀；
- 對於一個值，可以有唯一一個可變參考，或是任意數量的不可變參考——但絕不能兩者同時存在；
- 參考的存在時間不能超過它所指向的值。

為了實際看看借用檢查器的運作，讓我們試著打破第一條規則，在查票員仍在檢視卡片時將其回收：

```move
let card = purchase();
let card_ref = &card;

recycle(card); // 錯誤！區域變數 `card` 的移動無效：
               // 該值仍被 `card_ref` 借用中。

is_valid(card_ref);
```

編譯器會拒絕這個程式：只要 `card_ref` 仍然存在並被使用，它所指向的值就必須維持原位。同樣的機制也防止了兩個可變參考同時存在，或是在值被不可變借用時對其進行修改。多虧了這些規則，Move 中的參考永遠不可能指向已被銷毀或已被移走的資料，函式也因此可以信任其引數，而不需要任何執行期檢查。

## 依值傳遞 (Passing by Value) {#passing-by-value}

最後，讓我們說明當我們將值本身傳遞給函式時會發生什麼事。在這種情況下，函式會取得該值的所有權，使其在原本的範圍中無法再被存取。Card 的擁有者可以將其回收，藉此將所有權讓渡給函式。

```move file=packages/samples/sources/move-basics/references.move anchor=move

```

在 `recycle` 函式中，Card 是依值傳遞的，所有權因而轉移給該函式。這使得它可以被[拆解](./struct#unpacking-a-struct)並銷毀。

## 回傳參考 (Returning References) {#returning-references}

函式不僅可以接收參考——它也可以回傳參考。這正是我們在[結構體章節](./struct#getters-and-setters)中提到的 getter，用來讓其他模組存取結構體欄位的方式。讓我們為地鐵通行卡應用程式加入一個 getter：

```move file=packages/samples/sources/move-basics/references.move anchor=getter

```

被回傳的參考必須指向呼叫者所擁有的值——換句話說，它必須是從函式的其中一個參考參數所_衍生_出來的。回傳一個指向區域變數值的參考是不可能的，因為區域變數會在函式回傳時被銷毀：

```move
// 無法編譯！
public fun dangling(): &u8 {
    let x = 10;
    &x // 錯誤！區域變數 `x` 在函式結束時就被銷毀了。
}
```

回傳一個指向欄位的可變參考同樣是可行的——但這是一個需要謹慎斟酌的決定，因為它讓任何呼叫者都能直接修改該欄位。借用檢查器的規則同樣適用於被回傳的參考，如同它們適用於區域借用一般：只要被回傳的參考仍然存在，它所衍生自的那個值就會持續處於被借用狀態。

## 參考無法被儲存 (References Cannot Be Stored) {#references-cannot-be-stored}

Move 中的參考是_短暫存在_（ephemeral）的：它們存在於函式引數、區域變數以及回傳值中，但永遠無法被放入結構體中。參考型別的欄位是編譯錯誤，因此沒有任何值可以在函式呼叫結束後仍攜帶著參考。如果一個結構體需要長期參考另一個值，它會儲存該資料的一份副本或其識別碼，而絕不會儲存參考。

這項限制帶來的後果會在本書中反覆出現。這正是為什麼參考只具備 `copy` 和 `drop` [能力](./abilities-introduction)且永遠無法被儲存的原因；也是為什麼集合型別在每次呼叫 `borrow` 時都會給出一個全新的參考，而不是保留同一個參考。這同時也是為什麼 Move 不需要參考的_生命週期_（lifetime）標註的原因——參考永遠無法逃逸出建立它的那次呼叫。

## 解參考 (Dereferencing) {#dereferencing}

參考提供了對值的存取，但有時持有參考的程式碼需要值本身的一份副本。_解參考運算子_（dereference operator）`*` 會讀取參考背後的值，並產生它的一份副本——原始的值則保持不變、留在原處：

```move file=packages/samples/sources/move-basics/references.move anchor=deref

```

因為解參考會進行複製，所以只有具備[複製能力](./copy-ability)的型別才被允許這樣做——一個獨一無二的資產無法透過對它取得參考再解參考來達成複製。範例中的 `*(&mut ...) = value` 形式，是同一運算子的另一面：透過可變參考進行賦值，會取代其背後的值。

你也可能會遇到 `*&` 這樣的組合——先借用再立即解參考——這是撰寫欄位或變數之明確複本的慣用寫法。

## 實務中的借用：方法呼叫 (Borrowing in Practice: Method Calls) {#borrowing-in-practice-method-calls}

為了說明整個應用程式的完整流程，讓我們在一個測試中把所有片段組合起來。這次我們將使用[方法語法](./struct-methods)，而不是純粹的函式呼叫：

```move file=packages/samples/sources/move-basics/references.move anchor=move_2024

```

請注意，這個測試中沒有出現任何一個 `&`，然而參考其實正在背後完成所有的工作。當一個函式以方法語法被呼叫時，編譯器會根據該函式的簽章_自動_借用接收者：`card.is_valid()` 以 `&Card` 的形式不可變地借用 `card`，`card.enter_metro()` 以 `&mut Card` 的形式可變地借用它，而 `card.recycle()` 則是依值傳遞該值本身。這正是為什麼日常的 Move 程式碼很少明確寫出借用運算子的原因——大多數的借用都是在方法呼叫的地方隱式發生的，並遵循前面所述相同的借用檢查器規則。

## 總結 (Summary) {#summary}

- 參考允許在不放棄所有權的情況下將值展示給函式：`&` 用於唯讀存取，`&mut` 用於可讀寫存取。
- 借用檢查器強制執行安全規則：借用中的值不能被移動、只能有唯一一個 `&mut` _或_任意數量的 `&`，且任何參考的存在時間都不能超過它所指向的值。
- 函式可以回傳從其參考參數所衍生出的參考——這正是 getter 的基礎。
- 參考無法被儲存在結構體中——它們永遠不會存活超過該次函式呼叫。
- 方法呼叫會根據函式簽章自動借用接收者。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考手冊中的[參考](./../../reference/primitive-types/references)。
