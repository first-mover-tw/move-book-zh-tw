---
description: 地址型別 (Address Type) 在 Move 中：字面值、具名地址、轉換函式，以及地址如何在 Sui 上識別帳戶與套件。
---

# 地址型別 (Address Type) {#address-type}

Move 使用一種稱為 [address](./../concepts/address) 的特殊型別來表示地址——用來識別區塊鏈上帳戶、套件與物件的 32 位元組值。在運算式中，地址字面量以 `@` 符號開頭，後面接十六進位數字或識別字：

```move file=packages/samples/sources/move-basics/address.move anchor=address_literal

```

十六進位數字會被解讀為一個 32 位元組值，缺少的前導位元組會以零填補——所以 `@0x2` 是以 `...0002` 結尾的地址的簡寫。識別字會在 [Move.toml](./../concepts/manifest) 檔案中被查找，並由編譯器替換為對應的地址；如果找不到，編譯就會失敗。

> 有些地址是系統保留的：例如 [Standard Library](./standard-library) 位於 `0x1`，Sui Framework 位於 `0x2`。完整清單請見 [附錄 B：保留地址 (Appendix B: Reserved Addresses)](./../appendix/reserved-addresses)。

## 轉換 (Conversion) {#conversion}

Sui Framework 提供一組輔助函式來處理地址。由於地址型別是一個 32 位元組值，它可以轉換為 `u256` 型別，反之亦然。它也可以與 `vector<u8>` 型別互相轉換。

> 下方範例使用 [vector](./vector) 與 [String](./string) 型別，這些會在本章稍後介紹——目前只需知道與位元組、文字之間的轉換是存在的即可。

範例：將地址轉換為 `u256` 型別，並轉換回來。

```move file=packages/samples/sources/move-basics/address.move anchor=to_u256

```

範例：將地址轉換為 `vector<u8>` 型別，並轉換回來。

```move file=packages/samples/sources/move-basics/address.move anchor=to_bytes

```

範例：將地址轉換為字串。

```move file=packages/samples/sources/move-basics/address.move anchor=to_string

```

## 延伸閱讀 (Further Reading) {#further-reading}

- Move Reference 中的 [Address](./../../reference/primitive-types/address)。
- [sui::address](https://docs.sui.io/references/framework/sui/address) 模組文件。
