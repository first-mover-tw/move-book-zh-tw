---
title: 巧妙錯誤訊息 (Clever Errors) | 參考手冊
description: 巧妙錯誤 (Clever errors) 是一項功能，可在斷言 (assertion) 失敗或引發中止 (abort) 時提供更豐富的錯誤訊息
---

# 巧妙錯誤 (Clever Errors) {#clever-errors}

巧妙錯誤是一項功能，可在斷言（assertion）失敗或觸發 abort 時提供更豐富的錯誤訊息。它們是一種原始碼層級的功能，會編譯為 `u64` 型別的 abort code 值，其中包含存取行號、常數名稱與常數值所需的資訊（前提是要有該巧妙錯誤程式碼以及宣告該巧妙錯誤常數的模組）。由於這種編譯方式，需要經過後處理才能從 `u64` abort code 值還原成人類可讀的錯誤訊息。這項後處理由 Sui GraphQL 伺服器與 Sui CLI 自動完成。如果你想手動解碼巧妙 abort code，可以使用 [還原巧妙 Abort Code (Inflating Clever Abort Codes)](#inflating-clever-abort-codes) 中概述的流程來進行。

> 巧妙錯誤包含原始碼行號資訊以及其他資料。因此，其值可能會因原始檔案的任何變動而改變（例如自動格式化、新增模組成員，或新增換行）。

## 巧妙中止碼 (Clever Abort Codes) {#clever-abort-codes}

巧妙中止碼讓你可以使用非 `u64` 常數作為中止碼，只要該常數有標註 `#[error]` 屬性即可。這種常數既可用於斷言，也可用於 `abort` 的中止碼。

```move
module 0x42::a_module;

#[error]
const EIsThree: vector<u8> = b"The value is three";

// 如果 `x` 為 3 則會以 `EIsThree` 中止
public fun double_except_three(x: u64): u64 {
    assert!(x != 3, EIsThree);
    x * x
}

// 一律會以 `EIsThree` 中止
public fun clever_abort() {
    abort EIsThree
}
```

在這個範例中，`EIsThree` 常數是一個 `vector<u8>`，而非 `u64`。然而，`#[error]` 屬性讓這個常數可以被當作中止碼使用，並且在執行期會產生一個保存以下內容的 `u64` 中止碼值：

1. 一個表示此中止碼為巧妙中止碼的設定位元（tag-bit）。
2. 中止發生所在原始檔案的行號（例如 7）。
3. 該常數名稱在模組識別字表（identifier table）中的索引（例如 `EIsThree`）。
4. 該常數值在模組常數表中的索引（例如 `b"The value is three"`）。

以十六進位表示，若呼叫 `double_except_three(3)`，會以如下的 `u64` 中止碼中止：

```
0x8000_0007_0001_0000
  ^       ^    ^    ^
  |       |    |    |
  |       |    |    |
  |       |    |    +-- 常數值索引 = 0 (b"The value is three")
  |       |    +-- 常數名稱索引 = 1 (EIsThree)
  |       +-- 行號 = 7（斷言所在的行號）
  +-- 標籤位元 = 0b1000_0000_0000_0000
```

並且可以渲染成人類可讀的錯誤訊息，例如：

```
Error from '0x42::a_module::double_except_three' (line 7), abort 'EIsThree': "The value is three"
```

此訊息的確切格式可能因解碼此巧妙錯誤所使用的工具鏈而有所不同，但只要配合錯誤發生所在的模組，`u64` 中止碼中就包含了產生上述人類可讀錯誤訊息所需的全部資訊。

> 巧妙中止碼的值*不*需要是 `vector<u8>` —— 它可以是 Move 中任何有效的常數型別。

## 明確錯誤碼 (Explicit Error Codes) {#explicit-error-codes}

預設情況下，clever error 完全從原始碼推導其識別資訊 -- abort 所在的行號，以及常數的名稱與值。`#[error]` 屬性也接受一個明確的 `code` 引數，寫作 `#[error(code = <n>)]`，用來為錯誤附加開發者自訂的代碼：

```move
module 0x42::a_module;

/// 嘗試用相同的 parent-key 組合建立兩次同一個物件。
#[error(code = 0)]
const EObjectAlreadyExists: vector<u8> = b"Derived object is already claimed.";
```

這個 code 是一個無符號 8-bit 整數，儲存在 `u64` abort code 中屬於它自己的欄位，與行號以及常數的名稱與值分開。行號會在原始檔案變動時跟著改變，但 code 不同，它是由開發者固定的，因此能為每個錯誤提供一個穩定的數字識別碼，供工具顯示與比對。當 code 存在時，解碼器會將它與渲染出的訊息一起顯示，例如：

```
Error from '0x42::a_module::claim' (line 22), error code 0, 'EObjectAlreadyExists': "Derived object is already claimed."
```

常數的名稱與值仍會被記錄下來，因此人類可讀的訊息渲染方式與純 `#[error]` 相同。以這種方式指定明確的 code 是 Sui Framework 全程使用的慣例，其中每個 module 都會為其錯誤常數賦予小而穩定的 code。

## 無中止碼的斷言 (Assertions with no Abort Codes) {#assertions-with-no-abort-codes}

沒有中止碼的斷言與 `abort` 陳述式，會自動從原始碼行號推導出一個中止碼，並以聰明錯誤格式編碼，其中常數名稱與常數值的資訊會各自填入 `0xffff` 的哨兵值。例如：

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

這兩者都會產生一個 `u64` 中止碼值，其中包含：

1. 一個已設定的標籤位元，用來表示此中止碼是一個聰明中止碼。
2. 發生中止的原始碼檔案中的行號（例如 6）。
3. 模組識別字表中常數名稱索引的哨兵值 `0xffff`。
4. 模組常數表中常數值索引的哨兵值 `0xffff`。

以十六進位表示，若呼叫 `assert_false(3)`，將以下列 `u64` 中止碼中止：

```
0x8000_0004_ffff_ffff
  ^       ^    ^    ^
  |       |    |    |
  |       |    |    |
  |       |    |    +-- 常數值索引 = 0xffff（哨兵值）
  |       |    +-- 常數名稱索引 = 0xffff（哨兵值）
  |       +-- 行號 = 4（斷言的連結）
  +-- 標籤位元 = 0b1000_0000_0000_0000
```

## Clever Errors and Macros 靈活的錯誤與巨集 (Clever Errors and Macros) {#clever-errors-and-macros}

Clever abort 程式碼中的行號資訊，是從發生 abort 位置的原始檔案推導而來的。具體來說，對於函式而言，這會是函式內的行號；然而對於巨集而言，這會是巨集被呼叫的位置。這在撰寫巨集時相當有用，因為它讓使用者在使用可能引發 abort 條件的巨集時，仍能取得有用的錯誤訊息。

```move
module 0x42::macro_exporter;

public macro fun assert_false() {
    assert!(false);
}

public macro fun abort_always() {
    abort
}

public fun assert_false_fun() {
    assert!(false); // 永遠會以此呼叫的行號中止
}

public fun abort_always_fun() {
    abort // 永遠會以此呼叫的行號中止
}
```

接著在使用這些巨集的模組中：

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
    assert_false_fun(); // 會以 `assert_false_fun` 中斷言的行號中止
}

fun invoke_abort_always_fun() {
    abort_always_fun(); // 會以 `abort_always_fun` 中 `abort` 的行號中止
}
```

## Inflating Clever Abort Codes 展開巧妙中止碼 (Inflating Clever Abort Codes) {#inflating-clever-abort-codes}

Precisely, the layout of a clever abort code is as follows:

```

|<tagbit>|<reserved>|<source line number>|<module identifier index>|<module constant index>|
+--------+----------+--------------------+-------------------------+-----------------------+
| 1-bit  | 15-bits  |       16-bits      |     16-bits             |        16-bits        |

```

請注意，Move abort 會附帶一些額外資訊 —— 在我們的情境中，重要的是發生錯誤的模組。這很重要，因為識別字索引與常數索引是相對於該模組的識別字表與常數表（若未設定則為 sentinel 值）。

此配置中標示為 _reserved_ 的高位元，當有提供 [`#[error(code = N)]`](#explicit-error-codes) 設定的顯式錯誤碼時，也會以獨立的 8-bit 欄位保存該值。

> 若要解碼一個巧妙中止碼，你需要知道發生錯誤的模組，前提是識別字索引或常數索引未被設為 sentinel 值 `0xffff`。

以下用虛擬碼示範如何解碼巧妙中止碼：

```rust
// MoveAbort 中可取得的資訊
let clever_abort_code: u64 = ...;
let (package_id, module_name): (PackageStorageId, ModuleName) = ...;

let is_clever_abort = (clever_abort_code & 0x8000_0000_0000_0000) != 0;

if is_clever_abort {
    // 取得行號、識別字索引與常數索引
    // 若識別字與常數索引設為 '0xffff'，代表是 sentinel 值
    let line_number = ((clever_abort_code & 0x0000_ffff_0000_0000) >> 32) as u16;
    let identifier_index = ((clever_abort_code & 0x0000_0000_ffff_0000) >> 16) as u16;
    let constant_index = ((clever_abort_code & 0x0000_0000_0000_ffff)) as u16;

    // 印出行錯誤訊息
    print!("Error from '{}::{}' (line {})", package_id, module_name, line_number);

    // 若兩者皆為 sentinel 值，就不需要印出任何內容或載入模組
    if identifier_index == 0xffff && constant_index == 0xffff {
        return;
    }

    // 只有在常數名稱與值不是 0xffff 時才需要
    let module: CompiledModule = fetch_module(package_id, module_name);

    // 印出常數名稱（如果有的話）
    if identifier_index != 0xffff {
        let constant_name = module.get_identifier_at_table_index(identifier_index);
        print!(", '{}'", constant_name);
    }

    // 印出常數值（如果有的話）
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
