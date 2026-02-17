---

description: "Fast path vs consensus in Sui: how owned objects skip consensus for faster transactions while shared objects require ordering."
---

# 快速路徑與共識 (Fast Path & Consensus)

物件模型允許根據物件的所有權類型而有不同的交易執行路徑。執行路徑決定了網路如何處理和驗證交易。

## 併發挑戰 (Concurrency Challenge)

區塊鏈面臨基本的併發挑戰：多方可能同時嘗試修改或訪問相同的數據。Sui 透過共識機制解決此問題。

## 快速路徑 (Fast Path)

並非所有交易都需要相同級別的驗證。例如，轉移擁有的物件可以透過「快速路徑」處理，因為只有所有者有權訪問。這避免了繁重的共識過程。

## 共識路徑 (Consensus Path)

訪問共享狀態（共享物件）的交易需要經過「共識」，以便在所有節點上對狀態更新達成一致，維持網路一致性。

## 物件擁有的物件 (Objects owned by Objects)

被其他物件擁有的物件遵循與父物件相同的規則。如果父物件是共享的，子物件本質上也是共享的。
