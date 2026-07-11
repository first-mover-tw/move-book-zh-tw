---
description: 開源 Move 函式庫指南：命名慣例、文件撰寫、測試,以及發布可重複使用的套件於 Sui。
---

# 開源函式庫 (Open Sourcing Libraries) {#open-sourcing-libraries}

開源函式庫是為 Move 生態系做出貢獻的絕佳方式。本指南將協助你了解如何開源函式庫、如何撰寫測試，以及如何為函式庫撰寫文件。

## README {#readme}

TODO: readme

## 具名地址 (Named Addresses) {#named-addresses}

TODO: named address

## 產生文件 (Generating Documentation) {#generating-documentation}

TODO: docgen

## 新增範例 (Adding Examples) {#adding-examples}

當發布一個預期會被使用的套件（例如 NFT 協議或函式庫）時，展示這個套件該如何使用是很重要的。這時範例就派上用場了。Move 並沒有針對範例的特殊功能，不過有一些慣例用來標示範例。首先，只有 sources 會被納入套件的位元組碼中，因此放在其他目錄的程式碼不會被納入，但仍然會被測試！

這也是為什麼把範例放進獨立的 `examples/` 目錄是個好主意。

```bash
sources/
    protocol.move
    library.move
tests/
    protocol_test.move
examples/
    my_example.move
Move.toml
```

## 標籤與發行版本（Git） (Tags and Releases (Git)) {#tags-and-releases-git}

TODO: tags and releases

## 與閉源相容的技巧 (Tricks to allow compatibility with closed source) {#tricks-to-allow-compatibility-with-closed-source}

TODO: compatibility via empty functions with signatures
