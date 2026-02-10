# 地址 (Address)

地址是區塊鏈上位置的唯一標識符。它用於標識[套件](./packages)、[帳戶](./what-is-an-account)和[物件](./../object/object-model)。地址具有 32 位元組的固定大小，通常表示為以 `0x` 為前綴的十六進制字串。地址不區分大小寫。

```move
0xe51ff5cd221a81c3d6e22b9e670ddf99004d71de4f769b0312b68c7c4872e2f1
```

上面的地址是一個有效地址的範例。它長 64 個字元（32 位元組）並以 `0x` 為前綴。

Sui 還具有用於標識標準套件和物件的預留地址。預留地址通常是易於記憶和輸入的簡單數值。例如，標準庫的地址是 `0x1`。短於 32 位元組的地址會在左側補零。

```move
0x1 = 0x0000000000000000000000000000000000000000000000000000000000000001
```

以下是一些預留地址的範例：

- `0x1` - Sui 標準庫的地址（別名 `std`）
- `0x2` - Sui 框架的地址（別名 `sui`）
- `0x6` - 系統 `Clock` 物件的地址

> 您可以在[附錄 B](../appendix/reserved-addresses) 中找到所有預留地址。

## 進一步閱讀

- Move 中的[地址類型](../move-basics/address)
- [sui::address 模組](https://docs.sui.io/references/framework/sui/address)
