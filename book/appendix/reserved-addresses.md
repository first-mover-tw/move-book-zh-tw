---
description:
  Sui 上的保留地址（Reserved addresses）：標準函式庫 (standard library, 0x1)、Sui 框架 (Sui
  framework, 0x2)、系統物件 (system objects)，以及其他固定地址指派。
---

# 附錄 B：保留地址 (Appendix B: Reserved Addresses) {#appendix-b-reserved-addresses}

保留地址是在 Sui 上具有特定用途的特殊地址。它們在不同環境之間保持不變，並用於特定的原生操作。

- `0x1` - [標準函式庫](./../move-basics/standard-library.md)的地址（別名 `std`）
- `0x2` - [Sui 框架](./../programmability/sui-framework.md)的地址（別名 `sui`）
- `0x5` - `SuiSystem` 物件的地址
- `0x6` - 系統[`Clock` 物件](./../programmability/epoch-and-time.md)的地址
- `0x8` - 系統[`Random` 物件](./../programmability/randomness.md)的地址
- `0xc` - 系統
  [`CoinRegistry` 物件](./../programmability/balance-and-coin.md#currency-and-the-coin-registry)的地址
- `0xd` - 系統 `DisplayRegistry` 物件的地址（參見
  [Object Display](./../programmability/display.md)）
- `0x403` - `DenyList` 系統物件的地址
- `0xacc` - 系統 `AccumulatorRoot` 物件的地址
