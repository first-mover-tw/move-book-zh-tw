---
description:
  在 Sui 上建立你的第一個 Move 套件 (package)：學習專案結構、撰寫模組 (module)、編譯程式碼，並使用 Move
  CLI 執行測試。
---

# 哈囉，世界！

在本章中，您將學習如何建立一個新的 Move 套件、編寫一個簡單的模組、編譯它，並使用 Move CLI 執行測試。請確保您已[安裝 Sui](./../before-we-begin/install-sui.md) 並設定好您的 [IDE 環境](./../before-we-begin/ide-support.md)。執行以下指令來測試 Sui 是否已正確安裝。

```bash
# 它應該會印出客戶端版本。例如：sui-client 1.22.0-036299745。
sui client --version
```

> Move CLI 是 Move 語言的命令列介面；它內建於 Sui 二進位檔中，並提供一組指令來管理套件、編譯和測試程式碼。

本章的結構如下：

- [建立新套件](#建立新套件)
- [目錄結構](#目錄結構)
- [編譯套件](#編譯套件)
- [執行測試](#執行測試)

## 建立新套件

為了建立一個新程式，我們將使用 `sui move new` 指令，後面接著應用程式的名稱。我們的第一個程式將命名為 `hello_world`。

> 注意：在本章及其他章節中，如果您看到程式碼區塊中的行以 `$` (錢字號) 開頭，表示後續的指令應在終端機中執行。錢字號不應被包含在內。這是終端機環境中顯示指令的常見方式。

```bash
$ sui move new hello_world
```

`sui move` 指令提供 Move CLI 的存取權限——這是一個內建的編譯器、測試執行器和 Move 相關的實用工具。 `new` 指令後面接著套件名稱，將在一個新資料夾中建立一個新套件。在我們的例子中，資料夾名稱是 "hello_world"。

我們可以查看該資料夾的內容，以確認套件已成功建立。

```bash
$ ls -l hello_world
Move.toml
sources
tests
```

## 目錄結構

Move CLI 將建立應用程式的鷹架，並預先建立目錄結構和所有必要檔案。讓我們看看裡面有什麼。

```plaintext
hello_world
├── Move.toml
├── sources
│   └── hello_world.move
└── tests
    └── hello_world_tests.move
```

### 清單文件 (Manifest)

`Move.toml` 檔案，又稱為[套件清單文件](./../concepts/manifest.md)，包含套件的定義和配置設定。Move 編譯器使用它來管理套件中繼資料、獲取依賴項並註冊具名地址。我們將在[概念](./../concepts/index.md)章節中詳細解釋它。

> 預設情況下，該套件有一個具名地址——套件的名稱。

```toml
[addresses]
hello_world = "0x0"
```

### 原始碼

`sources/` 目錄包含原始碼檔案。Move 原始碼檔案具有 _.move_ 副檔名，通常以檔案中定義的模組命名。例如，在我們的案例中，檔案名稱是 _hello_world.move_，並且 Move CLI 已經在裡面放置了註解掉的程式碼：

```move
/*
/// 模組：hello_world
module hello_world::hello_world;
*/
```

> `/*` 和 `*/` 是 Move 中的註解分隔符號。它們之間的所有內容都會被編譯器忽略，可用於文件或備註。我們在[基本語法](./../move-basics/comments.md)中解釋了所有註解程式碼的方法。

註解掉的程式碼是一個模組定義，它以關鍵字 `module` 開頭，後面跟著一個具名地址（或地址文字），以及模組名稱。模組名稱是模組的唯一識別符號，並且在套件內必須是唯一的。模組名稱用於從其他模組或交易中參考該模組。

<!-- And the module name has to be a valid Move identifier: alphanumeric with underscores to separate words. A common convention is to call modules (and functions) in snake_case - all lowercase, with underscores. Coding conventions are important for readability and maintainability of the code, we summarize them in the Coding Conventions section. -->

### 測試

`tests/` 目錄包含套件測試。編譯器在常規建置過程中會排除這些檔案，但在 _test_ 和 _dev_ 模式下會使用它們。測試是用 Move 編寫的，並標記有 `#[test]` 屬性。測試可以分組在單獨的模組中（通常稱為 _module_name_tests.move_），或在它們所測試的模組內部。

模組、匯入、常數和函式可以用 `#[test_only]` 進行註解。此屬性用於將模組、函式或匯入從建置過程中排除。當您想為測試加入輔助工具而不將它們包含在將發佈到鏈上的程式碼中時，這會很有用。

_hello_world_tests.move_ 檔案包含一個註解掉的測試模組模板：

```move
/*
#[test_only]
module hello_world::hello_world_tests;
// 取消註解此行以匯入模組
// use hello_world::hello_world;

const ENotImplemented: u64 = 0;

#[test]
fun test_hello_world() {
    // 成功
}

#[test, expected_failure(abort_code = hello_world::hello_world_tests::ENotImplemented)]
fun test_hello_world_fail() {
    abort ENotImplemented
}
*/
```

### 其他資料夾

此外，Move CLI 支援 `examples/` 資料夾。其中的檔案處理方式與放在 `tests/` 資料夾下的檔案類似——它們只在 _test_ 和 _dev_ 模式下建置。它們是用來展示如何使用套件或如何將其與其他套件整合的範例。最常見的用途是出於文件目的和函式庫套件。

## 編譯套件

Move 是一種編譯型語言，因此它需要將原始碼檔案編譯成 Move 位元組碼。它僅包含有關模組、其成員和型別所需的資訊，並排除註解和一些識別符（例如，常數的識別符）。

為了展示這些功能，讓我們將 _sources/hello_world.move_ 檔案的內容替換為以下內容：

```move file=packages/hello_world/sources/hello_world.move anchor=source

```

在編譯期間，程式碼被建置，但不會執行。編譯後的套件只包含可以由其他模組或在交易中呼叫的函式。我們將在[概念](./../concepts/index.md)章節中解釋這些概念。但現在，讓我們看看當我們執行 _sui move build_ 時會發生什麼。

```bash
# 從 `hello_world` 資料夾執行
$ sui move build

# 或者，如果您沒有 `cd` 進入該資料夾
$ sui move build --path hello_world
```

它應該在您的控制台輸出以下訊息。

```plaintext
UPDATING GIT DEPENDENCY https://github.com/MystenLabs/sui.git
INCLUDING DEPENDENCY Bridge
INCLUDING DEPENDENCY DeepBook
INCLUDING DEPENDENCY SuiSystem
INCLUDING DEPENDENCY Sui
INCLUDING DEPENDENCY MoveStdlib
BUILDING hello_world
```

在編譯期間，Move 編譯器會自動建立一個建置資料夾，其中放置所有已獲取和編譯的依賴項，以及當前套件模組的位元組碼。

> 如果您使用版本控制系統（例如 Git），則應忽略建置資料夾。例如，您應該使用 `.gitignore` 檔案並將 `build` 加入其中。

## 執行測試

在我們進行測試之前，我們應該新增一個測試。Move 編譯器支援用 Move 編寫的測試並提供執行環境。測試可以放在原始碼檔案和 `tests/` 資料夾中。測試標記有 `#[test]` 屬性，並會被編譯器自動發現。我們在[測試](./../move-basics/testing.md)部分深入解釋測試。

將 `tests/hello_world_tests.move` 的內容替換為以下內容：

```move file=packages/hello_world/tests/hello_world_tests.move anchor=test

```

這裡我們匯入了 `hello_world` 模組，並呼叫其 `hello_world` 函式來測試輸出確實是字串 "Hello, World!"。現在，既然我們已經準備好測試，就讓我們以測試模式編譯套件並執行測試。Move CLI 為此提供了 `test` 指令：

```bash
$ sui move test
```

輸出應該與以下內容相似：

```plaintext
INCLUDING DEPENDENCY Bridge
INCLUDING DEPENDENCY DeepBook
INCLUDING DEPENDENCY SuiSystem
INCLUDING DEPENDENCY Sui
INCLUDING DEPENDENCY MoveStdlib
BUILDING hello_world
Running Move unit tests
[ PASS    ] 0x0::hello_world_tests::test_hello_world
Test result: OK. Total tests: 1; passed: 1; failed: 0
```

如果您在套件資料夾外執行測試，您可以指定套件的路徑：

```bash
$ sui move test --path hello_world
```

您也可以透過指定字串來一次執行一個或多個測試。所有包含該字串的測試名稱都將被執行：

```bash
$ sui move test test_hello
```

## 後續步驟

在本節中，我們解釋了 Move 套件的基礎知識：其結構、清單文件、建置和測試流程。[在下一頁](./hello-sui)，我們將編寫一個應用程式，並了解程式碼的結構以及該語言能做什麼。

## 延伸閱讀

- [套件清單文件](./../concepts/manifest.md)部分
- [Move 參考文件](./../../reference/packages)中的套件
