---
title: 索引語法 (Index Syntax) | 參考
description: 'Move 索引語法參考 (Move Index Syntax Reference)：對自訂型別使用 bracket notation，搭配
  #[syntax(index)] attribute 以達成直覺的存取模式。'
---

# 索引語法 (Index Syntax)

Move 提供的語法屬性（syntax attributes）允許你定義看起來和感覺起來都像原生 Move 程式碼的操作，並將這些操作轉化為你提供的使用者定義。

我們的第一個語法方法 `index` 允許你定義一組操作，這些操作可以作為你的資料型別的自訂索引存取器，例如透過對應的索引操作標註函式，將矩陣元素存取為 `m[i,j]`。此外，這些定義是針對特定型別的，並且隱式地開放給任何使用該型別的程式設計師。

## 概覽與總結 (Overview and Summary)

首先，考慮一個使用向量的向量來表示其值的 `Matrix` 型別。你可以在 `borrow` 和 `borrow_mut` 函式上使用 `index` 語法標註來編寫一個小型庫，如下所示：

```move
module matrix::matrix;

public struct Matrix<T> { v: vector<vector<T>> }

#[syntax(index)]
public fun borrow<T>(s: &Matrix<T>, i: u64, j: u64): &T {
    vector::borrow(vector::borrow(&s.v, i), j)
}

#[syntax(index)]
public fun borrow_mut<T>(s: &mut Matrix<T>, i: u64, j: u64): &mut T {
    vector::borrow_mut(vector::borrow_mut(&mut s.v, i), j)
}

public fun make_matrix<T>(v: vector<vector<T>>):  Matrix<T> {
    Matrix { v }
}
```

現在，任何使用此 `Matrix` 型別的人都可以對其使用索引語法：

```move
let mut m = matrix::make_matrix(vector[
    vector[1, 0, 0],
    vector[0, 1, 0],
    vector[0, 0, 1],
]);

let mut i = 0;
while (i < 3) {
    let mut j = 0;
    while (j < 3) {
        if (i == j) {
            assert!(m[i, j] == 1, 1);
        } else {
            assert!(m[i, j] == 0, 0);
        };
        *(&mut m[i,j]) = 2;
        j = j + 1;
    };
    i = i + 1;
}
```

## 用法 (Usage)

正如範例所示，如果你定義了一個資料型別和相關的索引語法方法，任何人都可以透過在該型別的值上編寫索引語法來呼叫該方法：

```move
let mat = matrix::make_matrix(...);
let m_0_0 = mat[0, 0];
```

在編譯期間，編譯器會根據運算式的位置和可變用法，將這些轉換為適當的函式呼叫：

```move
let mut mat = matrix::make_matrix(...);

let m_0_0 = mat[0, 0];
// 轉換為 `copy matrix::borrow(&mat, 0, 0)`

let m_0_0 = &mat[0, 0];
// 轉換為 `matrix::borrow(&mat, 0, 0)`

let m_0_0 = &mut mat[0, 0];
// 轉換為 `matrix::borrow_mut(&mut mat, 0, 0)`
```

你也可以將索引運算式與欄位存取混合使用：

```move
public struct V { v: vector<u64> }

public struct Vs { vs: vector<V> }

fun borrow_first(input: &Vs): &u64 {
    &input.vs[0].v[0]
    // 轉換為 `vector::borrow(&vector::borrow(&input.vs, 0).v, 0)`
}
```

### 索引函式接受靈活的參數 (Index Functions Take Flexible Arguments)

請注意，除了本章其餘部分描述的定義和型別限制外，Move 對你的索引語法方法作為參數接受的值沒有任何限制。這允許你在定義索引語法時實作複雜的程式行為，例如一個在索引超出範圍時接受預設值的資料結構：

```move
#[syntax(index)]
public fun borrow_or_set<Key: copy, Value: drop>(
    input: &mut MTable<Key, Value>,
    key: Key,
    default: Value
): &mut Value {
    if (contains(input, key)) {
        borrow(input, key)
    } else {
        insert(input, key, default);
        borrow(input, key)
    }
}
```

現在，當你索引進入 `MTable` 時，你也必須提供一個預設值：

```move
let string_key: String = ...;
let mut table: MTable<String, u64> = m_table::make_table();
let entry: &mut u64 = &mut table[string_key, 0];
```

這種可延伸的能力允許你為自己的型別編寫精確的索引介面，具體地強制執行自訂行為。

## 定義索引語法函式 (Defining Index Syntax Functions)

這種強大的語法形式允許你的所有使用者定義資料型別都以這種方式運作，前提是你的定義遵循以下規則：

1. `#[syntax(index)]` 屬性被新增到與主體型別定義在同一個模組中的指定函式上。
1. 指定的函式具有 `public` 能見度。
1. 函式接受一個參考型別作為其主體型別（其第一個參數），並傳回一個匹配的參考型別（如果主體是 `mut`，則傳回 `mut`）。
1. 每個型別只有一個可變定義和一個不可變定義。
1. 不可變和可變版本具有型別一致性：
   - 主體型別匹配，僅在可變性上有所不同。
   - 傳回型別與其主體型別的可變性匹配。
   - 型別參數（如果存在）在兩個版本之間具有相同的約束。
   - 除主體型別外的所有參數都相同。

以下內容和附加範例詳細描述了這些規則。

### 宣告 (Declaration)

要宣告一個索引語法方法，請在與主體型別定義相同的模組中，將 `#[syntax(index)]` 屬性新增到相關函式定義上方。這會向編譯器發出信號，表明該函式是指定型別的索引存取器。

#### 不可變存取器 (Immutable Accessor)

不可變索引語法方法是為唯讀存取而定義的。它接受主體型別的不可變參考，並傳回元素型別的不可變參考。`std::vector` 中定義的 `borrow` 函式就是一個例子：

```move
#[syntax(index)]
public native fun borrow<Element>(v: &vector<Element>, i: u64): &Element;
```

#### 可變存取器 (Mutable Accessor)

可變索引語法方法與不可變方法成對，允許讀取和寫入操作。它接受主體型別的可變參考，並傳回元素型別的可變參考。`std::vector` 中定義的 `borrow_mut` 函式就是一個例子：

```move
#[syntax(index)]
public native fun borrow_mut<Element>(v: &mut vector<Element>, i: u64): &mut Element;
```

#### 能見度 (Visibility)

為了確保索引函式在任何使用該型別的地方都可用，所有索引語法方法都必須具有公開（public）能見度。這確保了在 Move 的模組和套件中都能人體工學地使用索引。

#### 無重複 (No Duplicates)

除了上述要求外，我們限制每個主體基本型別只能定義一個不可變參考的索引語法方法和一個可變參考的索引語法方法。例如，你不能為多載（polymorphic）型別定義一個專門化版本：

```move
#[syntax(index)]
public fun borrow_matrix_u64(s: &Matrix<u64>, i: u64, j: u64): &u64 { ... }

#[syntax(index)]
public fun borrow_matrix<T>(s: &Matrix<T>, i: u64, j: u64): &T { ... }
    // 錯誤！Matrix 已經有一個不可變索引語法方法的定義
```

這確保了你始終可以分辨出哪個方法被呼叫，而無需檢查型別實例化。

### 型別約束 (Type Constraints)

預設情況下，索引語法方法具有以下型別約束：

**其主體型別（第一個參數）必須是對與標註函式定義在同一個模組中的單一型別的參考。** 這意味著你不能為元組、型別參數或值定義索引語法方法：

```move
#[syntax(index)]
public fun borrow_fst(x: &(u64, u64), ...): &u64 { ... }
    // 錯誤，因為主體型別是元組

#[syntax(index)]
public fun borrow_tyarg<T>(x: &T, ...): &T { ... }
    // 錯誤，因為主體型別是型別參數

#[syntax(index)]
public fun borrow_value(x: Matrix<u64>, ...): &u64 { ... }
    // 錯誤，因為 x 不是參考
```

**主體型別必須與傳回型別的可變性匹配。** 此限制允許你釐清將索引運算式借用為 `&vec[i]` 與 `&mut vec[i]` 時的預期行為。Move 編譯器使用可變性標記來確定呼叫哪個借用形式以產生適當可變性的參考。因此，我們不允許主體和傳回可變性不同的索引語法方法：

```move
#[syntax(index)]
public fun borrow_imm(x: &mut Matrix<u64>, ...): &u64 { ... }
    // 錯誤！可變性不相容
    // 預期傳回型別為可變參考 '&mut'
```

### 型別相容性 (Type Compatibility)

在定義不可變和可變索引語法方法對時，它們受多個相容性約束限制：

1. 它們必須接受相同數量的型別參數，且這些型別參數必須具有相同的約束。
1. 型別參數必須 _按位置_（而非按名稱）以相同的方式使用。
1. 它們的主體型別必須除可變性外完全匹配。
1. 它們的傳回型別必須除可變性外完全匹配。
1. 所有其他參數型別必須完全匹配。

這些約束是為了確保索引語法無論在可變還是不可變位置其行為都完全相同。

為了說明其中一些錯誤，回顧之前的 `Matrix` 定義：

```move
#[syntax(index)]
public fun borrow<T>(s: &Matrix<T>, i: u64, j: u64): &T {
    vector::borrow(vector::borrow(&s.v, i), j)
}
```

以下所有可變版本的定義都是型別不相容的：

```move
#[syntax(index)]
public fun borrow_mut<T: drop>(s: &mut Matrix<T>, i: u64, j: u64): &mut T { ... }
    // 錯誤！此處 `T` 具有 `drop` 約束，但在不可變版本中沒有

#[syntax(index)]
public fun borrow_mut(s: &mut Matrix<u64>, i: u64, j: u64): &mut u64 { ... }
    // 錯誤！此處接受的型別參數數量不同

#[syntax(index)]
public fun borrow_mut<T, U>(s: &mut Matrix<U>, i: u64, j: u64): &mut U { ... }
    // 錯誤！此處接受的型別參數數量不同

#[syntax(index)]
public fun borrow_mut<U>(s: &mut Matrix<U>, i_j: (u64, u64)): &mut U { ... }
    // 錯誤！此處接受的參數數量不同

#[syntax(index)]
public fun borrow_mut<U>(s: &mut Matrix<U>, i: u64, j: u32): &mut U { ... }
    // 錯誤！`j` 是不同的型別
```

同樣地，這裡的目標是使不可變和可變版本的使用保持一致。這允許索引語法方法在運作時無需根據可變與不可變用法改變行為或約束，最終確保一致的編程介面。
