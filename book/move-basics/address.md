---
description: 'The address type in Move: literals, named addresses, conversion functions, and how addresses identify accounts and packages on Sui.'
---

# 位址類型

Move 使用一種名為 [位址](./../concepts/address) 的特殊類型來表示位址。它是一個 32 位元組的值，可以表示區塊鏈上的任何位址。位址可以兩種形式書寫：以 `0x` 為前綴的十六進位位址，以及具名位址。

```move file=packages/samples/sources/move-basics/address.move anchor=address_literal

```

位址字面值以 `@` 符號開頭，後接一個十六進位數字或一個識別符號。十六進位數字被解釋為一個 32 位元組的值。識別符號會在 [Move.toml](./../concepts/manifest) 檔案中查找，並由編譯器替換為對應的位址。如果在 Move.toml 檔案中找不到該識別符號，編譯器將會拋出錯誤。

## 轉換

Sui 框架提供了一組輔助函式來處理位址。鑑於位址類型是一個 32 位元組的值，它可以轉換為 `u256` 類型，反之亦然。它也可以與 `vector<u8>` 類型之間進行轉換。

範例：將位址轉換為 `u256` 類型並反向轉換。

```move file=packages/samples/sources/move-basics/address.move anchor=to_u256

```

範例：將位址轉換為 `vector<u8>` 類型並反向轉換。

```move file=packages/samples/sources/move-basics/address.move anchor=to_bytes

```

範例：將位址轉換為字串。

```move file=packages/samples/sources/move-basics/address.move anchor=to_string

```

## 延伸閱讀

- Move 參考手冊中的 [位址](./../../reference/primitive-types/address)。
- [sui::address](https://docs.sui.io/references/framework/sui/address) 模組文件。
