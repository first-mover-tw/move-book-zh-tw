---
title: 巧妙錯誤 (Clever Errors) | 參考手冊
description: 智慧錯誤 (Clever errors) 是一項功能，可在斷言失敗或引發中止時提供更多資訊的錯誤訊息
keywords:
  - Move
  - Sui
  - Move reference
  - clever
  - errors
  - reference
  - error handling
questions:
  - How does Clever Errors work in Move?
  - What is the syntax for Clever Errors in Move?
  - What is Clever Abort Codes in Move?
  - What is Explicit Error Codes in Move?
answer: Clever errors are a feature that allows for more informative error messages when an assertion fails or an abort is raised
goal:
  description: Reader understands clever errors are a feature that allows for more informative error messages when an assertion fails or an abort is raised
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

# 巧妙錯誤 (Clever Errors) {#clever-errors}

巧妙錯誤是一項功能，可在斷言失敗或引發中止時提供更具資訊性的錯誤訊息。它們是原始碼功能，會編譯為 `u64` 中止碼值，其中包含根據巧妙錯誤碼以及宣告該巧妙錯誤常數的模組，存取行號、常數名稱與常數值所需的資訊。由於這項編譯，必須經過後續處理，才能將 `u64` 中止碼值轉換為人類可讀的錯誤訊息。Sui GraphQL 伺服器與 Sui CLI 都會自動執行後續處理。若你想手動解碼巧妙中止碼，可使用 [Inflating Clever Abort Codes](#inflating-clever-abort-codes) 中概述的流程。

> 巧妙錯誤除了其他資料外，還包含原始碼行資訊。因此，其值可能會因原始碼文件的任何變更而改變（例如自動格式化、新增模組成員，或新增換行）。

## 巧妙中止碼 (Clever Abort Codes) {#clever-abort-codes}

巧妙中止碼可讓你使用非 `u64` 常數作為中止碼，只要該常數以 `#[error]` 屬性
標註即可。它們可同時用於斷言，以及作為 `abort` 的碼。

```move
module 0x42::a_module;

#[error]
const EIsThree: vector<u8> = b"The value is three";

// 若 `x` 為 3，將以 `EIsThree` 中止
public fun double_except_three(x: u64): u64 {
    assert!(x != 3, EIsThree);
    x * x
}

// 一律會以 `EIsThree` 中止
public fun clever_abort() {
    abort EIsThree
}
```

在此範例中，`EIsThree` 常數是 `vector<u8>`，並非 `u64`。不過，
`#[error]` 屬性允許將該常數用作中止碼，並會在執行階段產生一個
`u64` 中止碼值，其中包含：

1. 用來表示該中止碼為巧妙中止碼的已設定標籤位元。
2. 中止在原始碼文件中發生的位置行號（例如 7）。
3. 模組識別字表中該常數名稱的索引（例如 `EIsThree`）。
4. 模組常數表中該常數值的索引（例如 `b"The value is three"`）。

以十六進位表示，若呼叫 `double_except_three(3)`，它將以下列 `u64` 中止碼中止：

```
0x8000_0007_0001_0000
  ^       ^    ^    ^
  |       |    |    |
  |       |    |    |
  |       |    |    |
  |       |    |    +-- 常數值索引 = 0 (b"The value is three")
  |       |    +-- 常數名稱索引 = 1 (EIsThree)
  |       +-- 行號 = 7（斷言所在行）
  +-- 標籤位元 = 0b1000_0000_0000_0000
```

並可呈現為人類可讀的錯誤訊息如下（例如）：

```
Error from '0x42::a_module::double_except_three' (line 7), abort 'EIsThree': "The value is three"
```

此訊息的確切格式可能因用於解碼巧妙錯誤的工具而異，但只要搭配發生錯誤的模組，
產生如上所示人類可讀錯誤訊息所需的所有資訊，都會存在於 `u64` 中止碼中。

> 巧妙中止碼值*不*需要是 `vector<u8>`──它可以是 Move 中任何有效的常數型別。

## 明確錯誤碼 (Explicit Error Codes) {#explicit-error-codes}

預設情況下，clever error 會完全從原始碼衍生其識別資訊——中止所在的行，
以及常數的名稱和值。`#[error]` 屬性也接受明確的 `code` 引數，寫法為
`#[error(code = <n>)]`，可將開發者選擇的代碼附加至錯誤：

```move
module 0x42::a_module;

/// 嘗試使用相同的父項-鍵組合建立兩次物件。
#[error(code = 0)]
const EObjectAlreadyExists: vector<u8> = b"Derived object is already claimed.";
```

此代碼是無號 8 位元整數，並儲存在 `u64` 中止碼自己的欄位內，與行號及
常數的名稱和值分開。不同於每當原始碼文件變更時就會偏移的行號，代碼由
開發者固定指定，因此為每個錯誤提供穩定的數值識別碼，工具可顯示並比對它。
存在代碼時，解碼器會將其與呈現的訊息一併顯示，例如：

```
Error from '0x42::a_module::claim' (line 22), error code 0, 'EObjectAlreadyExists': "Derived object is already claimed."
```

常數的名稱和值仍會被記錄，因此人類可讀的訊息會如同單獨使用 `#[error]` 時
一樣呈現。以此方式指派明確代碼，是整個 Sui Framework 採用的慣例；其中每個
模組都會為其錯誤常數提供簡短且穩定的代碼。

## 無中止碼的斷言 (Assertions with no Abort Codes) {#assertions-with-no-abort-codes}

沒有中止碼的斷言與 `abort` 陳述式，會自動從原始碼行號推導出中止碼，並以巧妙錯誤格式編碼；常數名稱與常數值資訊會各自填入 `0xffff` 的哨兵值。例如：

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

1. 已設定的標籤位元，表示中止碼是巧妙中止碼。
2. 原始碼文件中發生中止位置的行號（例如 6）。
3. 模組識別字表中常數名稱索引的 `0xffff` 哨兵值。
4. 模組常數表中常數值索引的 `0xffff` 哨兵值。

以十六進位表示，若呼叫 `assert_false(3)`，它會以下列 `u64` 中止碼中止：

```
0x8000_0004_ffff_ffff
  ^       ^    ^    ^
  |       |    |    |
  |       |    |    |
  |       |    |    |
  |       |    |    +-- 常數值索引 = 0xffff（哨兵值）
  |       |    +-- 常數名稱索引 = 0xffff（哨兵值）
  |       +-- 行號 = 4（斷言所在行）
  +-- 標籤位元 = 0b1000_0000_0000_0000
```

## 巧妙的錯誤與巨集 (Clever Errors and Macros) {#clever-errors-and-macros}

巧妙中止碼中的行號資訊，取自發生中止位置的原始碼檔案。特別是，對於函式而言，這會是函式內的行號；但對於巨集而言，這會是呼叫巨集的位置。在撰寫巨集時，這相當實用，因為它讓使用者能使用可能引發中止條件的巨集，同時仍取得實用的錯誤訊息。

```move
module 0x42::macro_exporter;

public macro fun assert_false() {
    assert!(false);
}

public macro fun abort_always() {
    abort
}

public fun assert_false_fun() {
    assert!(false); // 一律會以此呼叫的行號中止
}

public fun abort_always_fun() {
    abort // 一律會以此呼叫的行號中止
}
```

接著，在使用這些巨集的模組中：

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

## 巧妙中止碼的展開 (Inflating Clever Abort Codes) {#inflating-clever-abort-codes}

精確而言，巧妙中止碼的配置如下：

```

|<tagbit>|<reserved>|<source line number>|<module identifier index>|<module constant index>|
+--------+----------+--------------------+-------------------------+-----------------------+
| 1-bit  | 15-bits  |       16-bits      |     16-bits             |        16-bits        |

```

請注意，Move 中止會附帶一些額外資訊——在本例中最重要的是發生錯誤的
模組。這很重要，因為識別字索引和常數索引是相對於該模組的識別字與常數表
（若未設定則為哨兵值）。

此配置標示為 _保留_ 的高位元，也會在提供明確錯誤碼時，以專用的 8 位元欄位保存透過
[`#[error(code = N)]`](#explicit-error-codes) 設定的明確錯誤碼。

> 若識別字索引或常數索引其中之一未設為哨兵值 `0xffff`，你必須知道發生錯誤的模組，
> 才能解碼巧妙中止碼。

使用虛擬碼時，你可以如下解碼巧妙中止碼：

```rust
// MoveAbort 中可取得的資訊
let clever_abort_code: u64 = ...;
let (package_id, module_name): (PackageStorageId, ModuleName) = ...;

let is_clever_abort = (clever_abort_code & 0x8000_0000_0000_0000) != 0;

if is_clever_abort {
    // 取得行號、識別字索引與常數索引
    // 若設為 '0xffff'，識別字和常數索引會是哨兵值
    let line_number = ((clever_abort_code & 0x0000_ffff_0000_0000) >> 32) as u16;
    let identifier_index = ((clever_abort_code & 0x0000_0000_ffff_0000) >> 16) as u16;
    let constant_index = ((clever_abort_code & 0x0000_0000_0000_ffff)) as u16;

    // 印出行錯誤訊息
    print!("Error from '{}::{}' (line {})", package_id, module_name, line_number);

    // 若兩者皆為哨兵值，無須印出任何內容或載入模組
    if identifier_index == 0xffff && constant_index == 0xffff {
        return;
    }

    // 僅在常數名稱和值皆非 0xffff 時才需要
    let module: CompiledModule = fetch_module(package_id, module_name);

    // 印出常數名稱（若有）
    if identifier_index != 0xffff {
        let constant_name = module.get_identifier_at_table_index(identifier_index);
        print!(", '{}'", constant_name);
    }

    // 印出常數值（若有）
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
