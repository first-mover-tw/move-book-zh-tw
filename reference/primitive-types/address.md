---
title: 地址 (Address) | 參考手冊
description: Move 地址類型 (address type) 參考手冊：256 位元識別碼、具名地址、十六進位常值及地址相關操作。
keywords:
  - Move
  - Sui
  - Move reference
  - address
  - reference
questions:
  - How does Address work in Move?
  - What is the syntax for Address in Move?
  - What is Addresses and Their Syntax in Move?
  - What is Named Addresses in Move?
answer: 'Move address type reference: 256-bit identifiers, named addresses, hex literals, and address-related operations.'
goal:
  description: 'Reader understands move address type reference: 256-bit identifiers, named addresses, hex literals, and address-related operations'
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

`address` 是 Move 內建型別，用於表示儲存體中的位置（有時稱為帳戶）。`address` 值是 256 位元（32 位元組）的識別碼。Move 使用地址來區分 [模組](./../modules)套件，其中每個套件都有自己的地址和模組。特定的 Move 部署也可能將 `address` 值用於[儲存體](./../abilities#key)操作。

> 在 Sui 中，`address` 用於表示「帳戶」，以及透過強型別包裝器表示物件（使用 `sui::object::UID` 和 `sui::object::ID`）。

雖然 `address` 底層是 256 位元整數，但 Move 地址刻意設計為不透明：它們無法從整數建立、不支援算術運算，也無法修改。特定的 Move 部署可能有 `native` 函式來啟用其中部分操作（例如，從位元組 `vector<u8>` 建立 `address`），但這些不是 Move 語言本身的一部分。

雖然有執行階段地址值（型別為 `address` 的值），但它們 _不能_ 用於在執行階段存取模組。

## 地址及其語法 (Addresses and Their Syntax) {#addresses-and-their-syntax}

地址分為兩種：具名或數值。具名地址的語法遵循 Move 中任何具名識別字的相同規則。數值地址的語法不限於十六進位編碼值，任何有效的 [`u256` 數值](./integers)都可以作為地址值；例如，`42`、`0xCAFE` 和 `10_000` 都是有效的數值地址常值。

為了區分地址是否用於運算式情境，使用地址時的語法會依其使用情境而異：

- 當地址作為運算式使用時，地址必須加上 `@` 字元前綴，也就是 [`@<numerical_value>`](./integers) 或 `@<named_address_identifier>`。
- 在運算式情境之外，地址可以不寫開頭的 `@` 字元，也就是 [`<numerical_value>`](./integers) 或 `<named_address_identifier>`。

一般而言，你可以將 `@` 視為一個運算子，將地址從命名空間項目轉為運算式項目。

## 具名地址 (Named Addresses) {#named-addresses}

具名地址是一項功能，允許在任何使用地址的位置以識別字取代數值，而不僅限於值層級。具名地址會在 Move 套件中宣告並繫結為最上層元素（位於模組和指令碼之外），或作為引數傳遞給 Move 編譯器。

具名地址只存在於原始語言層級，並會在位元碼層級完全替換為其值。因此，應透過模組的具名地址，而非編譯期間指派給具名地址的數值，來存取模組及其成員。因此，雖然 `use my_addr::foo` 等同於 `use 0x2::foo`（若 `my_addr` 被指派為 `0x2`），但最佳實務是始終使用 `my_addr` 名稱。

### 範例 (Examples) {#examples}

```move
// 下列值的縮寫形式
// 0x0000000000000000000000000000000000000000000000000000000000000001
let a1: address = @0x1;
// 下列值的縮寫形式
// 0x0000000000000000000000000000000000000000000000000000000000000042
let a2: address = @0x42;
// 下列值的縮寫形式
// 0x00000000000000000000000000000000000000000000000000000000DEADBEEF
let a3: address = @0xDEADBEEF;
// 下列值的縮寫形式
// 0x000000000000000000000000000000000000000000000000000000000000000A
let a4: address = @0x0000000000000000000000000000000A;
// 將具名地址 `std` 的值指派給 `a5`
let a5: address = @std;
// 任何有效的數值都可作為地址使用
let a6: address = @66;
let a7: address = @42_000;

module 66::some_module {   // 不在運算式情境中，因此不需要 @
    use 0x1::other_module; // 不在運算式情境中，因此不需要 @
    use std::vector;       // 可以使用具名地址作為命名空間項目
    ...
}

module std::other_module {  // 宣告模組時可以使用具名地址
    ...
}
```
