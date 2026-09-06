---
description: Move 中的 std::internal 模組 (module)：使用 Permit<T> 將泛型函式呼叫 (generic function calls) 限制為定義型別 (type) T 的模組 (module)。
title: 內部許可 (Internal Permit)
keywords:
  - Move
  - Sui
  - Move tutorial
  - internal
  - permit
questions:
  - What is Internal Permit in Move?
  - How do I use Internal Permit in Move?
  - What is The Problem in Move?
  - What is The Permit Type in Move?
answer: 'The std::internal module in Move: use Permit<T> to restrict generic function calls to the module that defines the type T.'
goal:
  description: 'Reader understands the std::internal module in Move: use Permit<T> to restrict generic function calls to the module that defines the type T'
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

# 內部許可 (Internal Permit) {#internal-permit}

在 [使用 Struct 的自訂型別](./struct#field-visibility)章節中，我們建立了一條適用於 Move 各處的規則：只有定義型別的模組可以存取其欄位、封裝它以及解封裝它。這使定義模組成為其型別的唯一權限主體——所有其他原始碼都必須透過該模組選擇公開的函式。

不過，一旦泛型函式進入情境，這項權限似乎就會消失。公開泛型函式可以由*任何*模組以*任何*型別引數呼叫——定義該函式的函式庫無法得知呼叫端是否與其呼叫時使用的型別有任何關係。`std::internal` 模組彌補了這個缺口：它提供一個值，用以證明該呼叫已獲得定義該型別的模組授權。

## 問題 (The Problem) {#the-problem}

讓我們將問題具體化。假設我們想要建置一個型別登錄表——可讓型別以人類可讀名稱登錄的地方。一項自然的需求是：型別只能由定義它的模組登錄，因此沒有人能為其他人的型別宣稱名稱。

簽章的第一次嘗試會如下所示：

```move
/// 以指定的 `name` 登錄型別 `T`。
public fun register<T>(registry: &mut Registry, name: String) { /* ... */ }
```

此函式無法強制執行我們的需求。Move 無法在執行階段檢查呼叫者——沒有「取得呼叫模組」函式，這是刻意如此：函式的行為必須完全由其引數決定。但這種說法也指向了解決方案：如果無法觀察授權，就必須將它*傳入*——作為只有正確模組能夠產生的引數。

## Permit 型別 (The Permit Type) {#the-permit-type}

`std::internal` 模組很小——它定義了一個結構與一個函式：

```move
module std::internal;

/// `T` 型別的特權見證。
/// 執行個體只能由定義型別 `T` 的模組建立。
public struct Permit<phantom T>() has drop;

/// 為型別 `T` 建立新的 `Permit`。
/// 只能由定義型別 `T` 的模組呼叫。
public fun permit<T>(): Permit<T> { Permit() }
```

乍看之下，這裡沒有特別之處：一個沒有欄位的公開結構，以及任何人似乎都能夠呼叫的公開函式。重要的是註解中的主張——`permit<T>()` 只能由定義 `T` 的模組呼叫。一般的 Move 原始碼無法表達這種限制，而它確實也沒有在原始碼中表達：這是一項特殊規則，由編譯器以及套件發布至網路時的網路進行檢查。我們很快就會看到它的實際運作。

這個定義有兩項細節值得注意：

- 型別參數是 [phantom](./generics#phantom-type-parameters)——`Permit<T>` 不包含 `T`，因此可為某個型別建立許可，而無須建立該型別的執行個體。
- 唯一的能力是 `drop`：許可可以被捨棄，但無法複製或儲存。任何收到 `Permit<T>` 的人，都持有一項無法複製或藏起來供日後使用的證明。

## 使用 Permit (Using a Permit) {#using-a-permit}

若要讓這項規則生效，程式庫函式會將 `Permit<T>` 列為引數。這就是完整的
作法：由於只有定義 `T` 的模組能夠建立該值，接收它*即是*
授權。以下是問題陳述中已修正的登錄表：

```move file=packages/samples/sources/move-basics/internal-permit.move anchor=registry

```

`register` 函式甚至不會查看許可；`_permit` 中的底線表示它是
刻意未使用的。它的型別就是檢查機制。

> `std::internal` 與 `std::option` 和 `std::vector` 一樣，
> 都會被[隱式匯入](./standard-library#implicit-imports)，因此不需要 `use` 陳述式。建議的
> 樣式是保留模組前綴：在簽章中撰寫 `internal::Permit<T>`，並在
> 呼叫位置撰寫 `internal::permit<T>()`，而非直接匯入 `Permit`。

另一方面，定義型別的模組會建立許可並將其傳遞：

```move file=packages/samples/sources/move-basics/internal-permit-2.move anchor=use_permit

```

現在可以在測試中執行登錄：

```move file=packages/samples/sources/move-basics/internal-permit-2.move anchor=test

```

## 違反規則 (Breaking the Rule) {#breaking-the-rule}

是什麼阻止第三方模組為 `MyApp` 建立許可證，並以誤導性的名稱註冊它？讓我們試試看：

```move
module book::registry_intruder;

use book::registry_user::MyApp;
use book::type_registry::Registry;

public fun register_foreign_type(registry: &mut Registry) {
    let permit = internal::permit<MyApp>(); // 錯誤！
    registry.register(permit, "Not My App");
}
```

上述原始碼無法編譯：

```text
error[Sui E02011]: invalid internal permit call
  ┌─ sources/registry_intruder.move:7:18
  │
7 │     let permit = internal::permit<MyApp>();
  │                  ^^^^^^^^^^^^^^^^^^^^^^^^^
  │                  │                │
  │                  │                The type 'book::registry_user::MyApp' is not declared in the current module
  │                  Invalid call to an internal function. The function 'std::internal::permit' is
  │                  restricted to being called in the module that defines the type, 'book::registry_user'
```

這項檢查不只在編譯器中執行。在鏈上發布套件時，位元組碼驗證器也會強制執行相同規則，因此無法透過手動建立位元組碼或使用修改過的編譯器繞過它。已發布的 `Permit<T>` 是強而有力的保證：若函式收到一個許可證，便表示定義 `T` 的模組建立了它。

以這種方式受限制的型別參數稱為 _內部型別參數_，而 `permit` 並非唯一具有這類參數的函式：我們在[事件](./../programmability/events)與[儲存函式](./../storage/storage-functions)章節中介紹的 `sui::event::emit<T>` 和 `sui::transfer::transfer<T>`，也遵循相同規則。`std::internal` 所新增的是讓 _任何_ 函式庫都能要求這項保證的方法：這項特殊規則只適用於建立許可證，之後它會作為一般值傳遞給任何將其列為引數的函式。

## 為何採用此運作方式 (Why It Works This Way) {#why-it-works-this-way}

`Permit` 的設計遵循 Move 的一項通用原則：權限是由值來表示，而非透過執行階段檢查。函式藉由*持有*一個只能在授權位置建立的值，來證明自己獲准執行某項操作。這個概念遍布 Move 與 Sui——它是 [Witness](./../programmability/witness-pattern) 與
[Capability](./../programmability/capability) 模式的基礎——而 `Permit` 則是其最精簡的形式：一個標準的零欄位見證，表示「定義 `T` 的模組已核准此次呼叫」。

`Permit` 的能力經過選擇，以精確維持這項意義。沒有 `copy` 時，接收 permit 的函式無法複製它；沒有 `store` 時，便無法將它保留在鏈上並於稍後重複使用。此授權僅對目前的呼叫有效，之後便不復存在——每項特權操作都要求定義模組明確建立新的 permit。並且由於型別參數是 `phantom`，這項證明不需成本：不會建立、複製或消耗任何 `T` 的執行個體來產生它。

## 延伸閱讀 (Further Reading) {#further-reading}

- [std::internal](https://docs.sui.io/references/framework/std/internal) 模組文件。
- [見證者模式](./../programmability/witness-pattern) - `Permit` 背後更廣泛的模式。
