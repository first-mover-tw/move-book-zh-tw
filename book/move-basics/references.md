---
description: Move 中的參考 (References)：不可變與可變借用、借用檢查器，以及如何在不轉移擁有權的情況下安全傳遞值。
title: 參考資料 (References)
keywords:
  - Move
  - Sui
  - Move tutorial
  - references
questions:
  - What is References in Move?
  - How do I use References in Move?
  - What is The Metro Pass Application in Move?
  - What is Immutable References in Move?
answer: 'References in Move: immutable and mutable borrows, the borrow checker, and how to safely pass values without transferring ownership.'
goal:
  description: 'Reader understands references in Move: immutable and mutable borrows, the borrow checker, and how to safely pass values without transferring ownership'
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

# 參考 (References) {#references}

在 [所有權與範圍](./ownership-and-scope)章節中，我們說明了當值被傳遞給函式時，該值會被 _移動_ 至函式的範圍。這表示函式會成為該值的擁有者，而原始範圍（擁有者）將無法再使用它。這是 Move 中的重要概念，因為它確保值不會同時在多個地方被使用。然而，在某些使用案例中，我們想將值傳遞給函式，同時保留所有權。這正是參考派上用場之處。

為了說明這點，讓我們考慮一個簡單範例：捷運通行卡應用程式。我們會檢視卡片可能處於的 4 種不同情境：

1. 以固定價格在售票機購買
2. 向查票員出示，以證明乘客持有有效通行卡
3. 在閘門使用以進入捷運，並購買一次乘車
4. 在餘額用盡後回收

## 捷運通行卡應用程式 (The Metro Pass Application) {#the-metro-pass-application}

捷運通行卡應用程式的初始配置很簡單。我們定義 `Card` 型別，以及代表單張卡片乘車次數的 `USES` [常數](./constants)。我們也為卡片餘額用盡與卡片尚未用盡的情況加入[錯誤常數](./assert-and-abort#error-constants)。

```move file=packages/samples/sources/move-basics/references.move anchor=header_new
module book::metro_pass;


```

## 不可變參考 (Immutable References) {#immutable-references}

參考可讓你將值 _展示_ 給函式，而不必放棄所有權。在此例中，當我們向查票員出示 Card 時，不想放棄它的所有權，也不允許查票員耗用任何乘車次數。我們只想允許 _讀取_ Card 的值，並證明其所有權。

為此，我們在函式簽章中使用 `&` 符號，表示傳遞的是值的 _參考_，而非值本身。

```move file=packages/samples/sources/move-basics/references.move anchor=immutable

```

由於函式不會取得 Card 的所有權，因此可以 _讀取_ 其資料，但無法對它 _寫入_，也就是無法修改乘車次數。此外，函式簽章確保無法在未提供 Card 執行個體時呼叫它。這項重要特性使得 [Capability Pattern](./../programmability/capability) 成為可能，我們將在後續章節中介紹。

`&` 運算子不僅限於函式簽章：它是一個可套用至任何值或結構單一欄位的運算式。產生的參考可以儲存在區域變數中，並繼續傳遞：

```move
let card = purchase();

let card_ref = &card;       // 整個值的參考
let uses_ref = &card.uses;  // 單一欄位的參考
```

建立值的參考通常稱為「借用」該值。例如，取得 `Option` 包裝值參考的方法稱為 `borrow`。

## 可變參考 (Mutable Reference) {#mutable-reference}

在某些情況下，我們希望允許函式修改 Card。例如，在閘門使用 Card 時，我們需要扣除一次乘車。為達成此目的，我們會在函式簽章中使用 `&mut` 關鍵字。

```move file=packages/samples/sources/move-basics/references.move anchor=mutable

```

如同你在函式主體中所見，`&mut` 參考允許修改值，因此函式可以使用乘車次數。

可變參考可用於任何預期不可變參考的位置：將 `&mut card` 傳遞給 `is_valid` 函式完全沒有問題，該函式只是不會有能力修改該值。反過來則不成立：不可變參考絕不能轉換為可變參考。

## 借用檢查器 (The Borrow Checker) {#the-borrow-checker}

參考是在 _借用檢查器_ 的協助下編譯的；借用檢查器是編譯器的一部分，會追蹤每次借用，並拒絕可能不安全地使用參考的程式。它強制執行的規則如下：

- 當值被借用時，不能移動、按值傳遞或銷毀它；
- 一個值可以有單一可變參考，或任意數量的不可變參考，絕不能同時存在兩者；
- 參考的生命週期不得長於它所指向的值。

為了查看借用檢查器的運作，讓我們嘗試違反第一條規則：在查票員仍在查看卡片時回收它：

```move
let card = purchase();
let card_ref = &card;

recycle(card); // 錯誤！區域變數 `card` 的無效移動：
               // 該值仍由 `card_ref` 借用。

is_valid(card_ref);
```

編譯器會拒絕此程式：只要 `card_ref` 仍存在且被使用，它所指向的值就必須保留在原處。同一套機制也會防止兩個可變參考同時存在，或防止值在被不可變借用時遭到修改。多虧這些規則，Move 中的參考永遠不會指向已銷毀或已移走的資料，函式也能在不進行任何執行階段檢查的情況下信任其引數。

## 按值傳遞 (Passing by Value) {#passing-by-value}

最後，讓我們說明將值本身傳遞給函式時會發生什麼事。在此情況下，函式會取得該值的所有權，使其在原始範圍中無法存取。Card 的擁有者可以回收它，藉此將所有權交給函式。

```move file=packages/samples/sources/move-basics/references.move anchor=move

```

在 `recycle` 函式中，Card 是按值傳遞，將所有權轉移給函式。這讓它能夠被[解構](./struct#unpacking-a-struct)並銷毀。

## 回傳參考 (Returning References) {#returning-references}

函式不僅能接受參考，也能回傳參考。這正是我們在 [struct 章節](./struct#getters-and-setters)中提及的 _getter_ 如何讓其他模組存取結構欄位的方式。讓我們將一個 getter 加入捷運通行卡應用程式：

```move file=packages/samples/sources/move-basics/references.move anchor=getter

```

回傳的參考必須指向呼叫端擁有的值；換言之，它必須從函式的其中一個參考引數 _衍生_ 而來。無法回傳區域值的參考，因為函式回傳時會銷毀該區域值：

```move
// 無法編譯！
public fun dangling(): &u8 {
    let x = 10;
    &x // 錯誤！函式結束時會銷毀區域變數 `x`。
}
```

也可以回傳欄位的可變參考，但這項決定必須審慎做出，因為它允許任何呼叫端直接修改該欄位。借用檢查器規則對回傳參考的適用方式與區域借用相同：只要回傳參考仍存在，衍生出它的值就會持續被借用。

## 參考無法儲存 (References Cannot Be Stored) {#references-cannot-be-stored}

Move 中的參考是 _暫時性_ 的：它們可以作為函式引數、區域變數與回傳值存在，但絕不能放入結構中。參考型別的欄位會造成編譯錯誤，因此沒有任何值能在函式呼叫結束後攜帶參考。若結構需要長期指向另一個值，它會儲存資料的複本或其識別碼，而非參考。

你會在全書各處遇到此限制所帶來的影響。這就是參考僅具有 `copy` 與 `drop` [能力](./abilities-introduction)且無法被儲存的原因；也是集合型別會在每次 `borrow` 呼叫時提供新的參考，而非保留參考的原因。這也是 Move 的參考不需要 _生命週期_ 標註的原因：參考絕無法逸出建立它的呼叫。

## 解參考 (Dereferencing) {#dereferencing}

參考可讓你存取值，但有時持有參考的程式碼需要值本身的複本。_解參考運算子_ `*` 會讀取參考背後的值並產生其複本，原始值會維持原位且不受影響：

```move file=packages/samples/sources/move-basics/references.move anchor=deref

```

由於解參考會複製，因此只允許用於具有 [copy 能力](./copy-ability)的型別；無法藉由取得唯一資產的參考並解參考來複製它。範例中的 `*(&mut ...) = value` 形式是同一運算子的另一面：透過可變參考指派會取代其背後的值。

你也可能遇到 `*&` 組合，也就是借用後立即解參考；這是明確撰寫欄位或變數複本的慣用方式。

## 實務中的借用：方法呼叫 (Borrowing in Practice: Method Calls) {#borrowing-in-practice-method-calls}

為了說明應用程式的完整流程，讓我們在測試中將所有部分組合起來。這次我們會使用[方法語法](./struct-methods)，而非一般函式呼叫：

```move file=packages/samples/sources/move-basics/references.move anchor=move_2024

```

請注意，測試中完全沒有出現 `&`，但參考完成了所有工作。以方法語法呼叫函式時，編譯器會依據函式簽章 _自動_ 借用接收者：`card.is_valid()` 會以 `&Card` 不可變地借用 `card`，`card.enter_metro()` 會以 `&mut Card` 可變地借用它，而 `card.recycle()` 則會按原樣按值傳遞該值。這就是日常 Move 程式碼很少明確寫出借用運算子的原因：大多數借用都在方法呼叫位置隱含發生，並遵循上述相同的借用檢查器規則。

## 總結 (Summary) {#summary}

- 參考可讓函式查看值而不放棄所有權：`&` 用於唯讀存取，`&mut` 用於讀寫存取。
- 借用檢查器強制執行安全規則：不得移動已借用的值、單一 `&mut` _或_ 任意數量的 `&`，且參考不得比其值存活更久。
- 函式可以回傳從其參考引數衍生的參考，這是 getter 的基礎。
- 參考無法儲存在結構中，因此不會比函式呼叫存活更久。
- 方法呼叫會依據函式簽章自動借用接收者。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move Reference 中的 [References](./../../reference/primitive-types/references)。
