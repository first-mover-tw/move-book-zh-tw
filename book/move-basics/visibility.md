---

description: "Visibility modifiers in Move: private, public, public(package), and entry functions for controlling access to module members."
---

# 可見性修飾符

每個模組成員都有其可見性。預設情況下，所有模組成員都是 _私有的 (private)_ — 這意味著它們僅能在定義它們的模組內被存取。但是，您可以添加可見性修飾符來使模組成員變為 _公開的 (public)_ — 模組外部可見；或 _公開的（套件）(public(package))_ — 對同一個套件內的模組可見；或 _進入 (entry)_ — 可以從交易中呼叫，但不能從其他模組中呼叫。

## 內部可見性

在模組中定義且沒有可見性修飾符的函式或結構，對該模組而言是 _私有的_。它不能被其他模組呼叫。

```move
module book::internal_visibility;

// 此函式可以由同一個模組中的其他函式呼叫
fun internal() { /* ... */ }

// 同一個模組 -> 可以呼叫 internal()
fun call_internal() {
    internal();
}
```

以下程式碼將無法編譯：

<!-- TODO: 為範例添加失敗旗標 -->

```move
module book::try_calling_internal;

use book::internal_visibility;

// 不同的模組 -> 無法呼叫 internal()
fun try_calling_internal() {
    internal_visibility::internal();
}
```

請注意，僅僅是因為結構欄位從 Move 中不可見，並不意味著其值是保密的 — 始終可以從 Move 之外讀取鏈上物件的內容。您絕不應該在物件內部儲存未加密的秘密。

## 公開可見性

結構或函式可以透過在 `fun` 或 `struct` 關鍵字之前添加 `public` 關鍵字來變為 _公開的_。

```move
module book::public_visibility;

// 此函式可以從其他模組呼叫
public fun public_fun() { /* ... */ }
```

公開函式可以被匯入並從其他模組呼叫。以下程式碼將可以編譯：

```move
module book::try_calling_public;

use book::public_visibility;

// 不同的模組 -> 可以呼叫 public_fun()
fun try_calling_public() {
    public_visibility::public_fun();
}
```

與某些語言不同，結構欄位不能設置為公開的。

## 套件可見性

具有 _套件_ 可見性的函式可以從同一個套件內的任何模組呼叫，但不能從其他套件中的模組呼叫。換句話說，它對該套件而言是 _內部的_。

```move
module book::package_visibility;

public(package) fun package_only() { /* ... */ }
```

套件函式可以從同一個套件內的任何模組呼叫：

```move
module book::try_calling_package;

use book::package_visibility;

// 同一個套件 `book` -> 可以呼叫 package_only()
fun try_calling_package() {
    package_visibility::package_only();
}
```

## 原生函式

[框架](./../programmability/sui-framework) 和 [標準庫](./standard-library) 中的某些函式標有 `native` 修飾符。這些函式由 Move 虛擬機 (VM) 原生提供，在 Move 原始碼中沒有主體。要瞭解更多關於 `native` 修飾符的資訊，請參考 [Move 參考手冊](./../../reference/functions?highlight=native#native-functions)。

```move
module std::type_name;

public native fun get<T>(): TypeName;
```

這是來自 `std::type_name` 的一個例子，在 [反射章節](./type-reflection) 中可以瞭解更多關於此模組的資訊。

## 延伸閱讀

- Move 參考手冊中的 [可見性](./../../reference/functions#visibility)。
