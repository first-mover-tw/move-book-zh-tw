---
description: 在 Sui 上建立你的第一個 Move 套件：了解專案結構、撰寫模組、編譯程式碼，並使用 Move CLI 執行測試。
title: 你好，世界！
keywords:
  - Move
  - Sui
  - Move tutorial
  - hello
  - world
questions:
  - How do I create my first Move project?
  - How do I write Hello World in Move?
  - How do I compile and test Move code?
answer: Create a Move package with sui move new, write a module with a public function, compile with sui move build, and test with sui move test.
goal:
  description: Reader can create a Move package, write a module, compile it, and run tests
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

# 哈囉，世界！ (Hello, World!) {#hello-world}

在本章中，你將學習如何建立新的套件、撰寫簡單的模組、編譯它，並使用 Move CLI
執行測試。請確認你已[安裝 Sui](./../before-we-begin/install-sui.md)，並設定好你的
[IDE 環境](./../before-we-begin/ide-support.md)。執行以下命令以測試 Sui 是否已正確安裝。

```bash
# 應會印出用戶端版本。例如：sui-client 1.22.0-036299745。
sui client --version
```

> Move CLI 是 Move 語言的命令列介面；它內建於 Sui 二進位檔中，
> 提供一組用於管理套件、編譯及測試程式碼的命令。

本章結構如下：

- [建立新套件](#create-a-new-package)
- [目錄結構](#directory-structure)
- [編譯套件](#compiling-the-package)
- [執行測試](#running-tests)

## 建立新套件 (Create a New Package) {#create-a-new-package}

若要建立新程式，我們會使用 `sui move new` 命令，後面接上應用程式名稱。
我們的第一個程式將命名為 `hello_world`。

> 注意：在本章及其他章節中，如果你看到程式碼區塊中的行以 `$`（錢號）
> 開頭，表示應在終端機中執行其後的命令。不應包含該符號。這是在終端機環境中
> 顯示命令的常見方式。

```bash
$ sui move new hello_world
```

`sui move` 命令可存取 Move CLI——一個內建的編譯器、測試執行器及處理所有 Move
相關事務的工具。`new` 命令後接套件名稱，會在新的資料夾中建立新套件。
在此例中，資料夾名稱為「hello_world」。

我們可以檢視資料夾內容，確認套件已成功建立。

```bash
$ ls -l hello_world
Move.toml
sources
tests
```

## 目錄結構 (Directory Structure) {#directory-structure}

Move CLI 會建立應用程式骨架，並預先建立目錄結構及所有必要文件。讓我們看看裡面有什麼。

```plaintext
hello_world
├── Move.toml
├── sources
│   └── hello_world.move
└── tests
    └── hello_world_tests.move
```

### 套件清單 (Manifest) {#manifest}

稱為[套件清單](./../concepts/manifest.md)的 `Move.toml` 文件，包含套件的定義與
設定。Move Compiler 使用它來管理套件中繼資料、取得依賴項，以及註冊具名地址。
我們會在[概念](./../concepts/index.md)章節中詳細說明。

> 預設情況下，套件具有一個具名地址——即套件名稱。

```toml
[addresses]
hello_world = "0x0"
```

### 原始碼 (Sources) {#sources}

`sources/` 目錄包含原始碼文件。Move 原始碼文件使用 _.move_ 副檔名，
通常會以文件中定義的模組命名。例如，在此例中，文件名稱為
_hello_world.move_，且 Move CLI 已在其中放入已註解的程式碼：

```move
/*
/// 模組：hello_world
module hello_world::hello_world;
*/
```

> `/*` 和 `*/` 是 Move 中的註解分隔符號。兩者之間的所有內容都會被編譯器忽略，
> 可用於文件或附註。我們會在[基本語法](./../move-basics/comments.md)中說明
> 為程式碼加上註解的所有方式。

已註解的程式碼是模組定義；它以關鍵字 `module` 開頭，後接具名地址（或地址字面值）
及模組名稱。模組名稱是模組的唯一識別字，且必須在套件內保持唯一。模組名稱用於從
其他模組或交易參考該模組。

<!-- 模組名稱也必須是有效的 Move 識別字：可使用英數字元，並以底線分隔字詞。一種常見慣例是以 snake_case 命名模組（及函式）——全部使用小寫字母，並以底線分隔。程式碼慣例對程式碼的可讀性與可維護性很重要，我們會在程式碼撰寫慣例章節中加以總結。 -->

### 測試 (Tests) {#tests}

`tests/` 目錄包含套件測試。編譯器會在一般建置流程中排除這些文件，但會在 _test_
及 _dev_ 模式中使用它們。測試以 Move 撰寫，並以 `#[test]` 屬性標示。測試可以
集中於獨立模組中（通常命名為 _module_name_tests.move_），或放在其所測試的模組內。

模組、匯入、常數及函式都可以標註 `#[test_only]`。此屬性可用於將模組、函式或匯入
排除在建置流程之外。當你想為測試加入輔助工具，卻不想將它們納入會發布至鏈上的程式碼時，
這會很有用。

_hello_world_tests.move_ 文件包含已註解的測試模組範本：

```move
/*
#[test_only]
module hello_world::hello_world_tests;
// 取消註解此行以匯入模組
// use hello_world::hello_world;

const ENotImplemented: u64 = 0;

#[test]
fun test_hello_world() {
    // 通過
}

#[test, expected_failure(abort_code = hello_world::hello_world_tests::ENotImplemented)]
fun test_hello_world_fail() {
    abort ENotImplemented
}
*/
```

### 其他資料夾 (Other Folders) {#other-folders}

此外，Move CLI 支援 `examples/` 資料夾。該處的文件會以與置於 `tests/` 資料夾下
的文件類似方式處理——只會在 _test_ 及 _dev_ 模式中建置。它們用於展示如何使用套件，
或如何將其與其他套件整合。最常見的使用情境是文件用途及函式庫套件。

## 編譯套件 (Compiling the Package) {#compiling-the-package}

Move 是編譯式語言，因此需要將原始碼文件編譯為 Move 位元碼。它只包含模組、其成員
與型別的必要資訊，並排除註解及部分識別字（例如常數的識別字）。

為了展示這些功能，請將 _sources/hello_world.move_ 文件內容替換為以下內容：

```move file=packages/hello_world/sources/hello_world.move anchor=source

```

在編譯期間，程式碼會被建置，但不會執行。已編譯的套件只包含可由其他模組或交易中
呼叫的函式。我們會在[概念](./../concepts/index.md)章節中說明這些概念。
現在，讓我們看看執行 _sui move build_ 時會發生什麼事。

```bash
# 從 `hello_world` 資料夾執行
$ sui move build

# 或者，如果你沒有 `cd` 進入該資料夾
$ sui move build --path hello_world
```

你的主控台應會輸出以下訊息。

```plaintext
UPDATING GIT DEPENDENCY https://github.com/MystenLabs/sui.git
INCLUDING DEPENDENCY Bridge
INCLUDING DEPENDENCY DeepBook
INCLUDING DEPENDENCY SuiSystem
INCLUDING DEPENDENCY Sui
INCLUDING DEPENDENCY MoveStdlib
BUILDING hello_world
```

在編譯期間，Move Compiler 會自動建立建置資料夾，並在其中放置所有取得及編譯的
依賴項，以及目前套件模組的位元碼。

> 如果你使用 Git 等版本控制系統，應忽略建置資料夾。例如，你應使用 `.gitignore`
> 文件並將 `build` 加入其中。

## 執行測試 (Running Tests) {#running-tests}

在開始測試前，我們應該新增一項測試。Move Compiler 支援以 Move 撰寫的測試，
並提供執行環境。測試可放在原始碼文件及 `tests/` 資料夾中。測試以 `#[test]`
屬性標示，且編譯器會自動探索它們。我們會在[測試](./../move-basics/testing.md)
章節中深入說明測試。

請將 `tests/hello_world_tests.move` 的內容替換為以下內容：

```move file=packages/hello_world/tests/hello_world_tests.move anchor=test

```

此處我們匯入 `hello_world` 模組，並呼叫其 `hello_world` 函式，以測試輸出確實是
字串「Hello, World!」。現在測試已就緒，讓我們以測試模式編譯套件並執行測試。
Move CLI 為此提供了 `test` 命令：

```bash
$ sui move test
```

輸出應類似以下內容：

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

如果你在套件資料夾外執行測試，可以指定套件路徑：

```bash
$ sui move test --path hello_world
```

你也可以藉由指定字串，一次執行單一或多個測試。所有名稱包含該字串的測試都會執行：

```bash
$ sui move test test_hello
```

## 下一步 (Next Steps) {#next-steps}

在本節中，我們說明了 Move 套件的基本概念：其結構、套件清單、建置及測試流程。
[下一頁](./hello-sui)中，我們將撰寫一個應用程式，看看程式碼的結構以及此語言能做到什麼。

## 延伸閱讀 (Further Reading) {#further-reading}

- [套件清單](./../concepts/manifest.md)章節
- [The Move Reference](./../../reference/packages) 中的套件
