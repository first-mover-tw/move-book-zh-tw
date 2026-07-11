---
description: 'Struct methods in Move: use receiver syntax to call functions on struct instances with dot notation for cleaner code.'
---

# 結構方法 (Struct Methods)

Move 編譯器支援 **接收者語法 (receiver syntax)** `e.f()`，這允許定義可以在結構實例上呼叫的方法。術語「接收者」特別是指接收方法呼叫的實例。這與其他程式語言中的方法語法類似。這是定義操作結構欄位的函式的一種便捷方式，可以直接存取結構欄位，並建立比將結構作為參數傳遞更簡潔、更直觀的程式碼。

## 方法語法 (Method syntax)

如果函式的第一個參數是在定義該函式的模組內部的結構，那麼可以使用 `.` 運算子呼叫該函式。但是，如果第一個參數的類型是在另一個模組中定義的，則預設情況下該方法不會與該結構相關聯。在這種情況下，`.` 運算子語法不可用，必須使用標準的函式呼叫語法來呼叫該函式。

當匯入一個模組時，其方法會自動與該結構相關聯。

```move file=packages/samples/sources/move-basics/struct-methods.move anchor=hero

```

## 方法別名 (Method Aliases)

當模組定義了多個結構及其方法時，方法別名有助於避免名稱衝突。它們還可以為結構提供更具描述性的方法名稱。

語法如下：

```move
// 用於本地方法關聯
use fun function_path as Type.method_name;

// 導出的別名
public use fun function_path as Type.method_name;
```

> 僅允許為在同一個模組中定義的結構定義公開別名。對於在其他模組中定義的結構，仍然可以建立別名，但不能設置為公開。

在下面的範例中，我們更改了 `hero` 模組並添加了另一個類型 — `Villain`（反派）。`Hero` 和 `Villain` 都有類似的欄位名稱和方法。為了避免名稱衝突，我們分別在方法前加上了 `hero_` 和 `villain_` 前綴。但是，使用別名允許在結構實例上呼叫這些方法而無需前綴：

```move file=packages/samples/sources/move-basics/struct-methods-2.move anchor=hero_and_villain

```

在測試函式中，`health` 方法直接在 `Hero` 和 `Villain` 實例上呼叫而無需前綴，因為編譯器會自動將方法與其各自的結構相關聯。

> 注意：在測試函式中，`hero.health()` 是在呼叫別名方法，而不是直接存取私有的 `health` 欄位。雖然 `Hero` 和 `Villain` 結構是公開的，但它們的欄位對模組而言仍然是私有的。方法呼景 `hero.health()` 使用了由 `public use fun hero_health as Hero.health` 定義的公開別名，這提供了對私有欄位的受控存取。

## 延伸閱讀

- Move 參考手冊中的 [方法語法](./../../reference/method-syntax)。
