---

description: "Glossary of Move and Sui terminology: fast path, parallel execution, internal types, and other key concepts defined."
---

# 附錄 A: 術語表

- 快速路徑 (Fast Path) - 用來描述不涉及共享物件且無需共識即可執行的交易。
- 平行執行 (Parallel Execution) - 用來描述 Sui 執行時期 (runtime) 平行執行交易的能力，包括涉及共享物件的交易。
- 內部型別 (Internal Type) - 在模組內部定義的型別。此型別的欄位無法從模組外部存取，且在只有 "key" 能力的情況下，無法在 `public_*` 傳輸函數中使用。

## 能力 (Abilities)

- key - 允許結構體在儲存中用作鍵的能力。在 Sui 上，key 能力會標記一個物件，並要求第一個欄位為 `id: UID`。
- store - 允許結構體儲存於其他物件內部的能力。此能力放寬了對內部結構體的限制，允許 `public_*` 傳輸函數接受它們作為參數。它也使物件能夠作為動態欄位儲存。
- copy - 允許結構體被複製的能力。在 Sui 上，`copy` 能力與 `key` 能力衝突，且不能與其一同使用。
- drop - 允許結構體被忽略或丟棄的能力。在 Sui 上，`drop` 能力不能與 `key` 能力一同使用，因為物件不允許被忽略。