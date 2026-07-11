---
description: std::internal 模組 (module) 在 Move 中：使用 Permit<T> 將泛型函式呼叫限制在定義型別 T 的模組內。
---

# 內部授權 (Internal Permit) {#internal-permit}

在[使用結構自訂型別 (Custom Types with Struct)](./struct#field-visibility) 一節中，我們建立了一條在 Move 中隨處適用的規則：只有定義某個型別的模組才能存取其欄位、打包它，以及拆解它。這使得定義該模組成為該型別的唯一權威——所有其他程式碼都必須透過該模組選擇公開的函式來進行操作。

然而，一旦泛型函式登場，這種權威似乎就消失了。一個公開的泛型函式可以被*任何*模組以*任何*型別引數呼叫——定義該函式的函式庫無從得知呼叫者與被呼叫的型別是否有任何關聯。`std::internal` 模組填補了這個缺口：它提供了一個值，可以證明該次呼叫是由定義該型別的模組所授權的。

## 問題所在 (The Problem) {#the-problem}

讓我們把問題具體化。假設我們想建立一個型別註冊表——一個可以將型別註冊在人類可讀名稱下的地方。一個自然的要求是：型別只能由定義它的模組來註冊，這樣任何人都無法為別人的型別冒認名稱。

第一次嘗試的簽名大概會是這樣：

```move
/// 在給定的 `name` 底下註冊 `T` 型別。
public fun register<T>(registry: &mut Registry, name: String) { /* ... */ }
```

這個函式無法強制實施我們的要求。Move 沒有辦法在執行期檢視呼叫者——沒有「取得呼叫模組」這樣的函式，而這是刻意設計的：函式的行為必須完全由它的引數決定。但這句話同時也點出了解法：如果授權無法被觀察，它就必須被*傳入*——作為一個只有正確的模組才能產生的引數。

## Permit 型別 (The Permit Type) {#the-permit-type}

`std::internal` 模組非常精簡——它只定義了一個結構與一個函式：

```move
module std::internal;

/// `T` 型別的特權見證。
/// 實例只能由定義 `T` 型別的模組建立。
public struct Permit<phantom T>() has drop;

/// 為 `T` 型別建構一個新的 `Permit`。
/// 只能由定義 `T` 型別的模組呼叫。
public fun permit<T>(): Permit<T> { Permit() }
```

乍看之下，這裡什麼都沒有：一個沒有欄位的公開結構，以及一個任何人應該都能呼叫的公開函式。重要的部分在於註解中的宣稱——`permit<T>()` 只能由定義 `T` 的模組呼叫。一般的 Move 程式碼無法表達這樣的限制，事實上程式碼本身也沒有表達出來：這是一條特殊規則，由編譯器以及套件發布時的網路來檢查。我們馬上就會看到它的實際運作。

定義中有兩個值得注意的細節：

- 型別參數是 [phantom](./generics#phantom-type-parameters) 的——`Permit<T>` 並不包含一個 `T`，所以可以在不建構 `T` 實例的情況下為該型別建立 permit。
- 唯一的能力是 `drop`：permit 可以被捨棄，但不能被複製，也不能被儲存。任何收到 `Permit<T>` 的人，手上握有的是一個無法被複製或留待日後使用的證明。

## 使用 Permit (Using a Permit) {#using-a-permit}

要讓這條規則發揮作用，函式庫函式只需將 `Permit<T>` 列為引數。這就是全部的做法：由於只有定義 `T` 的模組才能建立這個值，收到它*本身*就是授權。以下是修正後、對應我們問題陳述的註冊表：

```move file=packages/samples/sources/move-basics/internal-permit.move anchor=registry

```

`register` 函式甚至沒有去檢視 permit——`_permit` 中的底線表示它是刻意不使用的。它的型別本身就是檢查機制。

> `std::internal` 和 `std::option`、`std::vector` 一樣，是[隱式匯入 (implicitly imported)](./standard-library#implicit-imports) 的——不需要 `use` 陳述式。建議的風格是保留模組前綴：在簽名中寫 `internal::Permit<T>`，在呼叫處寫 `internal::permit<T>()`，而不是直接匯入 `Permit`。

另一方面，定義型別的模組會建立一個 permit 並將其傳遞下去：

```move file=packages/samples/sources/move-basics/internal-permit-2.move anchor=use_permit

```

現在可以在測試中驗證這個註冊流程：

```move file=packages/samples/sources/move-basics/internal-permit-2.move anchor=test

```

## 打破規則 (Breaking the Rule) {#breaking-the-rule}

是什麼阻止了第三個模組為 `MyApp` 建立一個 permit，並用一個誤導性的名稱來註冊它？讓我們來試試看：

```move
module book::registry_intruder;

use book::registry_user::MyApp;
use book::type_registry::Registry;

public fun register_foreign_type(registry: &mut Registry) {
    let permit = internal::permit<MyApp>(); // ERROR!
    registry.register(permit, "Not My App");
}
```

以上程式碼將無法編譯：

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

這項檢查不僅止於編譯器。同一條規則也會在套件於鏈上發布時由位元組碼驗證器強制執行，因此無法透過手工打造位元組碼或使用修改過的編譯器來繞過。已發布的 `Permit<T>` 是一項牢固的保證：如果某個函式收到了它，那麼定義 `T` 的模組必定建立了它。

以這種方式受限的型別參數稱為*內部型別參數*，而 `permit` 並不是唯一擁有此特性的函式：`sui::event::emit<T>` 與 `sui::transfer::transfer<T>`（我們會在[事件 (Events)](./../programmability/events) 與[儲存函式 (Storage Functions)](./../storage/storage-functions) 章節中介紹）也遵循同樣的規則。`std::internal` 所新增的，是讓*任何*函式庫都能要求這項保證的方式：這條特殊規則只適用於 permit 的建立，從那之後，它就會作為一個普通的值，傳遞給任何將其列為引數的函式。

## 為何如此設計 (Why It Works This Way) {#why-it-works-this-way}

`Permit` 的設計遵循 Move 的一項通用原則：權限是由值來表示，而不是由執行期檢查來表示。一個函式要證明自己有權限做某件事，是透過*持有*一個只能在被授權之處才能建立的值。這個想法貫穿於 Move 與 Sui 中——它是[見證者模式 (Witness Pattern)](./../programmability/witness-pattern) 與[能力模式 (Capability)](./../programmability/capability) 的基礎——而 `Permit` 則是其最精簡的形式：一個標準、零欄位的見證者，意味著「定義 `T` 的模組核准了這次呼叫」。

`Permit` 的能力被選擇來維持這個含義的精確性。沒有 `copy`，收到 permit 的函式就無法複製它；沒有 `store`，它就無法被儲存在鏈上供日後重複使用。這項授權只在當次呼叫中有效，之後就會消失——每一次特權操作都需要定義模組明確地建立一個新的 permit。而且由於型別參數是 `phantom` 的，這項證明是免費的：不需要建立、複製或消耗任何 `T` 的實例來產生它。

## 延伸閱讀 (Further Reading) {#further-reading}

- [std::internal](https://docs.sui.io/references/framework/std/internal) 模組文件。
- [見證者模式 (Witness Pattern)](./../programmability/witness-pattern) —— `Permit` 背後更廣泛的模式。
