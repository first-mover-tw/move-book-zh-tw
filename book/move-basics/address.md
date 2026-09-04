---
description: Move 中的地址類型 (address type)：字面值 (literals)、具名地址 (named addresses)、轉換函式 (conversion functions)，以及地址 (addresses) 如何識別 Sui 上的帳戶 (accounts) 與套件 (packages)。
title: 地址類型 (Address Type)
keywords:
  - Move
  - Sui
  - Move tutorial
  - address
  - type
  - type system
questions:
  - What is Address Type in Move?
  - How do I use Address Type in Move?
  - What is Conversion in Move?
answer: 'The address type in Move: literals, named addresses, conversion functions, and how addresses identify accounts and packages on Sui.'
goal:
  description: 'Reader understands the address type in Move: literals, named addresses, conversion functions, and how addresses identify accounts and packages on Sui'
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

# 地址型別 (Address Type) {#address-type}

Move 使用一種名為 [address](./../concepts/address) 的特殊型別來表示地址——用於識別區塊鏈上帳戶、套件與物件的 32 位元組值。在運算式中，地址常值以 `@` 符號開頭，後面接十六進位數字或識別字：

```move file=packages/samples/sources/move-basics/address.move anchor=address_literal

```

十六進位數字會被解讀為 32 位元組值，缺少的前導位元組會以零補齊——因此，`@0x2` 是以 `...0002` 結尾之地址的簡寫。編譯器會在 [Move.toml](./../concepts/manifest) 文件中查詢識別字，並將其替換為對應地址；若找不到，編譯將會失敗。

> 有些地址由系統保留：例如，[Standard Library](./standard-library)
> 位於 `0x1`，而 Sui Framework 位於 `0x2`。完整清單請見
> [附錄 B：保留地址 (Appendix B: Reserved Addresses)](./../appendix/reserved-addresses)。

## 轉換 (Conversion) {#conversion}

Sui Framework 提供一組用於處理地址的輔助函式。由於地址型別是 32 位元組值，因此可與 `u256` 型別互相轉換，也可與 `vector<u8>` 型別互相轉換。

> 下列範例使用本章稍後會介紹的 [vector](./vector) 與 [String](./string) 型別——目前只需要知道，可以在位元組與文字之間進行轉換。

範例：將地址轉換為 `u256` 型別後再轉換回來。

```move file=packages/samples/sources/move-basics/address.move anchor=to_u256

```

範例：將地址轉換為 `vector<u8>` 型別後再轉換回來。

```move file=packages/samples/sources/move-basics/address.move anchor=to_bytes

```

範例：將地址轉換為字串。

```move file=packages/samples/sources/move-basics/address.move anchor=to_string

```

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的 [Address](./../../reference/primitive-types/address)。
- [sui::address](https://docs.sui.io/references/framework/sui/address) 模組文件。
