---
description: 'Understand Move packages — the unit of code organization containing modules, dependencies, and addresses published on the Sui blockchain.'
---

# 套件 (Package)

Move 是一種用於編寫智能合約的語言——智能合約是存儲並在區塊鏈上運行的程式。單個程式被組織成一個套件。套件發佈在區塊鏈上，並由一個[地址](./address)標識。已發佈的套件可以透過發送呼叫其函式的[交易](./what-is-a-transaction)來進行互動。它也可以作為其他套件的相依項。

> 要建立新套件，請使用 `sui move new` 命令。要了解有關該命令的更多資訊，請運行 `sui move new --help`。

套件由模組組成——包含函式、類型和其他項目的獨立作用域。

```
package 0x...
    module a
        struct A1
        fun hello_world()
    module b
        struct B1
        fun hello_package()
```

## 套件結構

在本地，套件是一個包含 `Move.toml` 檔案和 `sources` 目錄的目錄。`Move.toml` 檔案稱為「套件清單 (package manifest)」，包含有關套件的中繼資料，而 `sources` 目錄包含模組的原始程式碼。套件通常看起來像這樣：

```
sources/
    my_module.move
    another_module.move
    ...
tests/
    ...
examples/
    using_my_module.move
Move.toml
```

`tests` 目錄是可選的，包含套件的測試。放置在 `tests` 目錄中的程式碼不會發佈在鏈上，僅在測試中可用。`examples` 目錄可用於程式碼範例，同樣不會發佈在鏈上。

## 已發佈的套件

在開發期間，套件沒有地址，需要設置為 `0x0`。一旦套件發佈，它就會在區塊鏈上獲得一個唯一的[地址](./address)，其中包含其模組的位元組碼。已發佈的套件會變成「不可變 (immutable)」的，並可以透過發送交易來進行互動。

```
0x...
    my_module: <bytecode>
    another_module: <bytecode>
```

## 鏈結

- [專案清單](./manifest)
- [地址](./address)
- Move 參考手冊中的[套件](./../../reference/packages)。
