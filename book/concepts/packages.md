---
description: 理解 Move 套件 (Move packages) — 程式碼組織的單位，包含發布於 Sui 區塊鏈上的模組 (modules)、依賴項 (dependencies) 與地址 (addresses)。
---

# 套件 (Package) {#package}

Move 是一種用來撰寫智慧合約的語言——這些程式會被儲存並執行在區塊鏈上。
單一程式會被組織成一個套件。套件會被發佈到區塊鏈上，並由一個
[地址](./address) 識別。已發佈的套件可以透過發送
[交易](./what-is-a-transaction) 呼叫其函式來與之互動。它也可以作為
其他套件的依賴項。

> 要建立新套件，請使用 `sui move new` 指令。若要進一步了解此指令，請執行
> `sui move new --help`。

套件由多個模組組成——各自獨立的作用範圍，包含函式、型別與其他項目。

```
package 0x...
    module a
        struct A1
        fun hello_world()
    module b
        struct B1
        fun hello_package()
```

## 套件結構 (Package Structure) {#package-structure}

在本機端，套件是一個包含 `Move.toml` 檔案與 `sources` 目錄的資料夾。`Move.toml`
檔案——稱為「套件清單 (package manifest)」——包含套件的中繼資料，而 `sources`
目錄則包含模組的原始碼。套件通常會長得像這樣：

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

`tests` 目錄是選擇性的，包含此套件的測試。放在 `tests`
目錄中的程式碼不會被發佈到鏈上，只會在測試中可用。`examples` 目錄則
可用於程式碼範例，同樣不會被發佈到鏈上。

## 已發佈套件 (Published Package) {#published-package}

在開發階段，套件還沒有地址，此時會用 `0x0` 來代替。一旦
套件被發佈，它會在區塊鏈上取得一個唯一的[地址](./address)，其中包含其
模組的位元組碼 (bytecode)。已發佈的套件會變成 _不可變 (immutable)_，可以透過發送
交易與之互動。

```
0x...
    my_module: <bytecode>
    another_module: <bytecode>
```

雖然已發佈的位元組碼永遠無法被更改，但套件可以被 _升級 (upgraded)_：升級會
在新地址發佈套件的新版本，同時保留舊版本不變。我們會在本書中多處
談到這帶來的影響：[套件升級 (Package Upgrades)](./../programmability/package-upgrades)
章節說明了其運作機制，而
[可升級性實務做法 (Upgradeability Practices)](./../guides/upgradeability-practices) 指南則涵蓋了如何為
升級進行設計。

## 延伸閱讀 (Further Reading) {#further-reading}

- [套件清單 (Package Manifest)](./manifest)
- [地址 (Address)](./address)
- Move 參考手冊中的[套件 (Packages)](./../../reference/packages)。
