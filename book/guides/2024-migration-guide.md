---

description: "Migrate your Move code to the 2024 edition: updated syntax, new features, method syntax, and step-by-step migration instructions."
---

# Move 2024 遷移指南 (Move 2024 Migration Guide)

Move 2024 是由 Mysten Labs 維護的 Move 語言新版本。本指南旨在幫助您了解 2024 版本與之前版本 Move 語言之間的差異。

> 本指南提供了新版本變更的高層級概覽。如需更詳細且詳盡的變更列表，請參考 [Sui 官方文件](https://docs.sui.io/guides/developer/advanced/move-2024-migration)。

## 使用新版本

要使用新版本，您需要在 `Move.toml` 檔案中指定版本。在 `Move.toml` 檔案中使用 `edition` 關鍵字來指定版本。目前唯一可用的版本是 `2024.beta`。

```ini
edition = "2024"
# 或者，為了使用新功能：
edition = "2024.beta"
```

## 遷移工具 (Migration Tool)

Move CLI 具有一個遷移工具，可以將程式碼更新到新版本。要使用遷移工具，請運行以下命令：

```bash
$ sui move migrate
```

遷移工具將更新程式碼以使用 `let mut` 語法、結構的新 `public` 修飾符，以及使用 `public(package)` 函式可見性來取代 `friend` 宣告。

## 使用 `let mut` 進行可變綁定

Move 2024 引入了 `let mut` 語法來宣告可變變數。`let mut` 語法用於宣告一個在宣告後可以更改的可變變數。

> 現在可變變數必須使用 `let mut` 宣告。如果您嘗試在沒有 `mut` 關鍵字的情況下重新分配變數，編譯器將發出錯誤。

```move
// Move 2020
let x: u64 = 10;
x = 20;

// Move 2024
let mut x: u64 = 10;
x = 20;
```

此外，`mut` 關鍵字也用於元組解構和函式參數中，以宣告可變變數。

```move
// 按值獲取並變更
fun takes_by_value_and_mutates(mut v: Value): Value {
    v.field = 10;
    v
}

// `mut` 應放在變數名稱之前
fun destruct() {
    let (x, y) = point::get_point();
    let (mut x, y) = point::get_point();
    let (mut x, mut y) = point::get_point();
}

// 在結構解構中
fun unpack() {
    let Point { x, mut y } = point::get_point();
    let Point { mut x, mut y } = point::get_point();
}
```

## Friends 已被廢棄 (Deprecated)

在 Move 2024 中，`friend` 關鍵字已被廢棄。取而代之的是，您可以使用 `public(package)` 可見性修飾符，使函式對同一個套件中的其他模組可見。

```move
// Move 2020
friend book::friend_module;
public(friend) fun protected_function() {}

// Move 2024
public(package) fun protected_function_2024() {}
```

## 結構可見性 (Struct Visibility)

在 Move 2024 中，結構獲得了可見性修飾符。目前唯一可用的可見性修飾符是 `public`。

```move
// Move 2020
struct Book {}

// Move 2024
public struct Book {}
```

## 方法語法 (Method Syntax)

在新版本中，以結構作為第一個參數的函式會與該結構關聯。這意味著可以使用點號 (.) 表示法來呼叫該函式。在同一個模組中與該類型一起定義的方法會自動匯舉。

> 如果類型與方法定義在同一個模組中，方法會自動導出。不可能為其他模組中定義的類型導出方法。但是，您可以在模組作用域中建立[自定義別名](#method-aliases)。

```move
public fun count(c: &Counter): u64 { /* ... */ }

fun use_counter() {
    // move 2020
    let count = counter::count(&c);

    // move 2024
    let count = c.count();
}
```

## 內建類型的方法

在 Move 2024 中，一些原生和標準類型獲得了關聯方法。例如，`vector` 類型具有一個 `to_string` 方法，可將向量轉換為 UTF8 字串。

```move
fun aliases() {
    // vector 轉換為字串和 ASCII 字串
    let str: String = b"Hello, World!".to_string();
    let ascii: ascii::String = b"Hello, World!".to_ascii_string();

    // address 轉換為位元組
    let bytes = @0xa11ce.to_bytes();
}
```

有關內建別名的完整列表，請參考[標準庫](./../move-basics/standard-library#source-code)和 [Sui 框架](./../programmability/sui-framework#source-code)原始程式碼。

## 借用運算子 (Borrowing Operator)

一些內建類型支持借用運算子。借用運算子用於獲取指定索引處元素的參照。借用運算子定義為 `[]`。

```move
fun play_vec() {
    let v = vector[1,2,3,4];
    let first = &v[0];         // 呼叫 vector::borrow(v, 0)
    let first_mut = &mut v[0]; // 呼叫 vector::borrow_mut(v, 0)
    let first_copy = v[0];     // 呼叫 *vector::borrow(v, 0)
}
```

支持借用運算子的類型包括：

- `vector`
- `sui::vec_map::VecMap`
- `sui::table::Table`
- `sui::bag::Bag`
- `sui::object_table::ObjectTable`
- `sui::object_bag::ObjectBag`
- `sui::linked_table::LinkedTable`

要為自定義類型實作借用運算子，您需要為方法添加 `#[syntax(index)]` 屬性。

```move
#[syntax(index)]
public fun borrow(c: &List<T>, key: String): &T { /* ... */ }

#[syntax(index)]
public fun borrow_mut(c: &mut List<T>, key: String): &mut T { /* ... */ }
```

## 方法別名 (Method Aliases)

在 Move 2024 中，方法可以與類型關聯。別名可以針對任何類型在模組本地定義；如果類型在同一個模組中定義，則可以公開定義。

```move
// my_module.move
// 本地：類型對於模組來說是外部的
use fun my_custom_function as vector.do_magic;

// sui-framework/kiosk/kiosk.move
// 已導出：類型定義在同一個模組中
public use fun kiosk_owner_cap_for as KioskOwnerCap.kiosk;
```
