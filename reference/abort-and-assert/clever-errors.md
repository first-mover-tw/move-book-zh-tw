---
title: '聰明錯誤 | Reference'
description: 聰明錯誤是一項功能，可在斷言失敗或中止被觸發時提供更具資訊性的錯誤訊息
---

# 聰明錯誤 (Clever Errors)

聰明錯誤是一項功能，可在斷言失敗或中止被觸發時提供更具資訊性的錯誤訊息。它們是一項原始碼功能，編譯成 `u64` 中止碼值，包含存取行號、常數名稱和常數值所需的資訊，並根據宣告聰明錯誤常數的模組而定。由於這個編譯，需要進行後處理才能從 `u64` 中止碼值轉換為人類可讀的錯誤訊息。Sui GraphQL 伺服器以及 Sui CLI 會自動執行後處理。如果您想手動解碼聰明中止碼，可以使用 [擴展聰明中止碼](#inflating-clever-abort-codes) 中概述的流程進行。

> 聰明錯誤包含原始碼行號資訊和其他資料。因此，由於原始碼檔案的任何變更（例如自動格式化、新增模組成員或新增換行符號），其值可能會改變。

## 聰明中止碼 (Clever Abort Codes)

聰明中止碼允許您使用非 u64 常數作為中止碼，只要常數使用 `#[error]` 屬性進行標註即可。它們可同時用於斷言和作為 `abort` 的碼。

```move
module 0x42::a_module;

#[error]
const EIsThree: vector<u8> = b"The value is three";

// 如果 x 為 3，會使用 EIsThree 中止
public fun double_except_three(x: u64): u64 {
    assert!(x != 3, EIsThree);
    x * x
}

// 總是會使用 EIsThree 中止
public fun clever_abort() {
    abort EIsThree
}
```

在此範例中，`EIsThree` 常數是 `vector<u8>`，不是 `u64`。然而，`#[error]` 屬性允許常數作為中止碼使用，並在執行時產生 `u64` 中止碼值，其中包含：

1. 一個設定的標記位元，表示中止碼是聰明中止碼。
2. 中止發生在原始碼檔案中的行號（例如，7）。
3. 模組識別碼表中常數名稱的索引（例如，`EIsThree`）。
4. 模組常數表中常數值的索引（例如，`b"The value is three"`）。

以十六進位表示，如果呼叫 `double_except_three(3)`，它將以如下 `u64` 中止碼中止：

```
0x8000_0007_0001_0000
  ^       ^    ^    ^
  |       |    |    |
  |       |    |    |
  |       |    |    +-- 常數值索引 = 0 (b"The value is three")
  |       |    +-- 常數名稱索引 = 1 (EIsThree)
  |       +-- 行號 = 7 (斷言的行)
  +-- 標記位元 = 0b1000_0000_0000_0000
```

並可呈現為人類可讀的錯誤訊息，如（例如）

```
Error from '0x42::a_module::double_except_three' (line 7), abort 'EIsThree': "The value is three"
```

此訊息的確切格式可能因用於解碼聰明錯誤的工具而異，但當與發生錯誤的模組相結合時，`u64` 中止碼中包含生成類似上述人類可讀錯誤訊息所需的所有資訊。

> 聰明中止碼值不一定要是 `vector<u8>` -- 它可以是 Move 中的任何有效常數類型。

## 沒有中止碼的斷言 (Assertions with no Abort Codes)

沒有中止碼的斷言和 `abort` 陳述式會自動從原始碼行號推導中止碼，並以聰明錯誤格式編碼，其中常數名稱和常數值資訊將分別填入 `0xffff` 的哨兵值。例如，

```move
module 0x42::a_module;

#[test]
fun assert_false(x: bool) {
    assert!(false);
}

#[test]
fun abort_no_code() {
    abort
}
```

這兩者都會產生 `u64` 中止碼值，其中包含：

1. 一個設定的標記位元，表示中止碼是聰明中止碼。
2. 中止發生在原始碼檔案中的行號（例如，6）。
3. 常數名稱模組識別碼表索引的 `0xffff` 哨兵值。
4. 模組常數表中常數值索引的 `0xffff` 哨兵值。

以十六進位表示，如果呼叫 `assert_false(3)`，它將以如下 `u64` 中止碼中止：

```
0x8000_0004_ffff_ffff
  ^       ^    ^    ^
  |       |    |    |
  |       |    |    |
  |       |    |    +-- 常數值索引 = 0xffff (哨兵值)
  |       |    +-- 常數名稱索引 = 0xffff (哨兵值)
  |       +-- 行號 = 4 (斷言的行)
  +-- 標記位元 = 0b1000_0000_0000_0000
```

## 聰明錯誤和巨集 (Clever Errors and Macros)

聰明中止碼中的行號資訊是從發生中止的原始碼位置衍生而來的。特別是，對於函式，這會是函式內的行號，但對於巨集，這會是巨集被呼叫的位置。這在編寫巨集時非常有用，因為它為使用者提供了一種方式，讓他們使用可能引發中止條件的巨集，同時仍然獲得有用的錯誤訊息。

```move
module 0x42::macro_exporter;

public macro fun assert_false() {
    assert!(false);
}

public macro fun abort_always() {
    abort
}

public fun assert_false_fun() {
    assert!(false); // 總是會以此呼叫的行號中止
}

public fun abort_always_fun() {
    abort // 總是會以此呼叫的行號中止
}
```

然後在使用這些巨集的模組中：

```move
module 0x42::user_module;

use 0x42::macro_exporter::{
    assert_false,
    abort_always,
    assert_false_fun,
    abort_always_fun
};

fun invoke_assert_false() {
    assert_false!(); // 會以此呼叫的行號中止
}

fun invoke_abort_always() {
    abort_always!(); // 會以此呼叫的行號中止
}

fun invoke_assert_false_fun() {
    assert_false_fun(); // 會以 assert_false_fun 中的斷言行號中止
}

fun invoke_abort_always_fun() {
    abort_always_fun(); // 會以 abort_always_fun 中 abort 的行號中止
}
```

## 擴展聰明中止碼 (Inflating Clever Abort Codes) {#inflating-clever-abort-codes}

更精確地說，聰明中止碼的版面配置如下：

```

|<標記位元>|<保留>|<原始碼行號>|<模組識別碼索引>|<模組常數索引>|
+--------+----------+--------------------+-------------------------+-----------------------+
| 1-bit  | 15-bits  |       16-bits      |     16-bits             |        16-bits        |

```

請注意，Move 中止會附帶一些額外資訊 -- 在我們的情況下，重要的是發生錯誤的模組。這很重要，因為識別碼索引和常數索引相對於模組的識別碼和常數表（如果未設定，則為哨兵值）。

> 要解碼聰明中止碼，如果識別碼索引或常數索引未設定為 `0xffff` 的哨兵值，您需要知道發生錯誤的模組。

在虛擬程式碼中，您可以按如下方式解碼聰明中止碼：

```rust
// MoveAbort 中可用的資訊
let clever_abort_code: u64 = ...;
let (package_id, module_name): (PackageStorageId, ModuleName) = ...;

let is_clever_abort = (clever_abort_code & 0x8000_0000_0000_0000) != 0;

if is_clever_abort {
    // 取得行號、識別碼索引和常數索引
    // 如果設定為 '0xffff'，識別碼和常數索引為哨兵值
    let line_number = ((clever_abort_code & 0x0000_ffff_0000_0000) >> 32) as u16;
    let identifier_index = ((clever_abort_code & 0x0000_0000_ffff_0000) >> 16) as u16;
    let constant_index = ((clever_abort_code & 0x0000_0000_0000_ffff)) as u16;

    // 列印行錯誤訊息
    print!("Error from '{}::{}' (line {})", package_id, module_name, line_number);

    // 如果兩者都是哨兵值，不需要列印任何內容或載入模組
    if identifier_index == 0xffff && constant_index == 0xffff {
        return;
    }

    // 僅在常數名稱和值不是 0xffff 時需要
    let module: CompiledModule = fetch_module(package_id, module_name);

    // 列印常數名稱（如有）
    if identifier_index != 0xffff {
        let constant_name = module.get_identifier_at_table_index(identifier_index);
        print!(", '{}'", constant_name);
    }

    // 列印常數值（如有）
    if constant_index != 0xffff {
        let constant_value = module
            .get_constant_at_table_index(constant_index)
            .deserialize_on_constant_type()
            .to_string();

        print!(": {}", constant_value);
    }

    return;
}
```
