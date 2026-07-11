---
description: 瞭解 Sui 中的地址 (Address)——用於在區塊鏈上定位套件 (package)、帳戶與物件的 32 位元組唯一識別碼。
---

# 地址 (Address) {#address}

地址是區塊鏈上位置的唯一識別碼。它用來識別
[套件](./packages)、[帳戶](./what-is-an-account)與[物件](./../object/object-model)。
地址的固定大小為 32 位元組，通常以前綴 `0x` 的十六進位字串表示。地址不區分大小寫。

```move
0xe51ff5cd221a81c3d6e22b9e670ddf99004d71de4f769b0312b68c7c4872e2f1
```

上方的地址是一個有效地址的範例。它長度為 64 個字元（32 位元組），並帶有 `0x` 前綴。

Sui 也有保留地址，用來識別標準套件與物件。保留地址通常是簡單、容易記憶與輸入的值。例如，
標準函式庫的地址是 `0x1`。長度不足 32 位元組的地址會在左側補零。

```move
0x1 = 0x0000000000000000000000000000000000000000000000000000000000000001
```

以下是一些保留地址的範例：

- `0x1` - Move 標準函式庫的地址（別名 `std`）
- `0x2` - Sui Framework 的地址（別名 `sui`）
- `0x6` - 系統 `Clock` 物件的地址

> 你可以在
> [附錄 B：保留地址](../appendix/reserved-addresses) 中找到所有保留地址。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 中的[地址型別](../move-basics/address)
- [sui::address 模組](https://docs.sui.io/references/framework/sui/address)
