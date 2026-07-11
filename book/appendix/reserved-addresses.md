---
description:
  Sui 上的保留位址（Reserved addresses）：標準函式庫 (standard library, 0x1)、Sui 框架 (Sui
  framework, 0x2)、系統物件 (system objects)，以及其他固定位址指派。
---

# 附錄 B：保留位址 (Appendix B: Reserved Addresses) {#appendix-b-reserved-addresses}

保留位址是在 Sui 上具有特定用途的特殊位址。它們在不同環境之間保持不變，並用於特定的原生操作。

- `0x1` - [標準函式庫](./../move-basics/standard-library.md)的位址（別名 `std`）
- `0x2` - [Sui 框架](./../programmability/sui-framework.md)的位址（別名 `sui`）
- `0x5` - `SuiSystem` 物件的位址
- `0x6` - 系統[`Clock` 物件](./../programmability/epoch-and-time.md)的位址
- `0x8` - 系統[`Random` 物件](./../programmability/randomness.md)的位址
- `0xc` - 系統
  [`CoinRegistry` 物件](./../programmability/balance-and-coin.md#currency-and-the-coin-registry)的位址
- `0xd` - 系統 `DisplayRegistry` 物件的位址（參見
  [Object Display](./../programmability/display.md)）
- `0x403` - `DenyList` 系統物件的位址
- `0xacc` - 系統 `AccumulatorRoot` 物件的位址
