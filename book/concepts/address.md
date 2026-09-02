---
description: 了解 Sui 中的地址 (address) — 用於定位區塊鏈 (blockchain) 上的套件 (package)、帳戶 (account) 和物件 (object) 的 32 位元組 (byte) 唯一識別碼 (identifier)。
title: 地址 (Address)
keywords:
  - Move
  - Sui
  - Move tutorial
  - address
questions:
  - What is Address in Move?
  - How do I use Address in Move?
answer: Learn about addresses in Sui — 32-byte unique identifiers used to locate packages, accounts, and objects on the blockchain.
goal:
  description: Reader understands addresses in Sui — 32-byte unique identifiers used to locate packages, accounts, and objects on the blockchain
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

# 地址 (Address) {#address}

地址是區塊鏈上位置的唯一識別碼。它用於識別[套件](./packages)、[帳戶](./what-is-an-account)和[物件](./../object/object-model)。地址的固定大小為 32 位元組，通常表示為以 `0x` 為前綴的十六進位字串。地址不區分大小寫。

```move
0xe51ff5cd221a81c3d6e22b9e670ddf99004d71de4f769b0312b68c7c4872e2f1
```

上述地址是有效地址的範例。它長度為 64 個字元 (32 位元組)，並以 `0x` 為前綴。

Sui 也有保留地址，用於識別標準套件和物件。保留地址通常是易於記憶和輸入的簡單值。例如，標準函式庫的地址是 `0x1`。短於 32 位元組的地址會向左填充零。

```move
0x1 = 0x0000000000000000000000000000000000000000000000000000000000000001
```

以下是一些保留地址的範例：

- `0x1` - Move 標準函式庫的地址 (別名 `std`)
- `0x2` - Sui Framework 的地址 (別名 `sui`)
- `0x6` - 系統 `Clock` 物件的地址

> 你可以在[附錄 B：保留地址 (Appendix B: Reserved Addresses)](../appendix/reserved-addresses) 中找到所有保留地址。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 中的[地址型別 (Address type)](../move-basics/address)
- [sui::address 模組 (sui::address module)](https://docs.sui.io/references/framework/sui/address)
