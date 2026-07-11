---
description: 結構方法 (Struct Methods) — 使用接收者語法 (receiver syntax)，以點記法呼叫結構實例上的函式，讓程式碼更簡潔。
---

# 結構方法 (Struct Methods) {#struct-methods}

在前面的章節中，我們一直使用點運算子來呼叫值上的函式：
`v.length()`、`opt.is_some()`、`artist.name()`。這就是**接收者語法 (receiver syntax)** ——「接收者」指的是接收方法呼叫的實例——本節將解釋它的運作方式以及如何控制它。方法讓操作結構的程式碼讀起來更自然：值放在前面，接著是操作，而且不需要匯入或完整拼出函式所屬的模組。

## 方法語法 (Method Syntax) {#method-syntax}

核心規則：當一個函式的第一個參數是在**同一模組**中定義的結構時，該函式就可以用 `.` 運算子呼叫。這類方法會自動在該結構被使用的任何地方可用——這正是為什麼 `vector` 和 `Option` 的值一出現就能用點語法呼叫的原因。如果第一個參數的型別是在其他模組中定義的，該函式預設不會與結構關聯，必須使用標準的函式呼叫語法——除非如下所示宣告了**別名 (alias)**。

```move file=packages/samples/sources/move-basics/struct-methods.move anchor=hero

```

## 方法別名 (Method Aliases) {#method-aliases}

方法別名有助於在模組定義多個結構及其方法時避免名稱衝突。它們也可以為結構提供更具描述性的方法名稱。

以下是語法：

```move
// 用於本地方法關聯
use fun function_path as Type.method_name;

// 匯出的別名
public use fun function_path as Type.method_name;
```

> 公開別名只允許用於同一模組中定義的結構。對於在其他模組中定義的結構，仍然可以建立別名，但不能將其設為公開。

在下面的範例中，我們修改了 `hero` 模組並新增了另一個型別——`Villain`。`Hero` 和 `Villain` 都有類似的欄位名稱和方法。為了避免名稱衝突，我們分別為方法加上 `hero_` 和 `villain_` 前綴。然而，使用別名可以讓這些方法在結構實例上呼叫時不需要前綴：

```move file=packages/samples/sources/move-basics/struct-methods-2.move anchor=hero_and_villain

```

在測試函式中，`health` 方法直接在 `Hero` 和 `Villain` 實例上呼叫時不需要前綴，因為編譯器會自動將方法與其對應的結構關聯起來。

> 注意：在測試函式中，`hero.health()` 呼叫的是別名方法，而不是直接存取私有的 `health` 欄位。雖然 `Hero` 和 `Villain` 結構是公開的，但它們的欄位在模組內仍是私有的。方法呼叫 `hero.health()` 使用的是由
> `public use fun hero_health as Hero.health` 定義的公開別名，該別名提供了對私有欄位的受控存取。

## 為外部型別的方法建立別名 (Aliasing a Method of an External Type) {#aliasing-a-method-of-an-external-type}

別名不僅限於模組自身的結構：本地（非公開）別名可以將方法名稱附加到來自其他模組的型別上。這裡我們為標準的 `String` 型別增加了一個額外的方法名稱 `num_bytes`——這是一個更精確的名稱，用來描述其 `length` 函式實際計算的內容：

```move file=packages/samples/sources/move-basics/struct-methods-3.move anchor=string_alias

```

該別名只存在於宣告它的模組內——這正是為什麼它不能是 `public` 的：該模組並不擁有 `String` 型別，因此無法為其他所有人擴充它的介面。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[方法語法](./../../reference/method-syntax)。
