---
title: '索引語法 (Index Syntax) | 參考'
description: "Move 索引語法參考：使用中括號標記法搭配 #[syntax(index)] 屬性，為自訂型別提供直觀的存取模式。"
---

# 索引語法 (Index Syntax)

Move 提供語法屬性，讓你定義看起來和感覺就像原生 Move 程式碼的操作，並將這些操作降低轉換為由使用者提供的定義。

我們的第一個語法方法 `index`，可以讓你定義一組操作，作為資料型別的自訂索引存取器，例如以 `m[i,j]` 的方式存取矩陣元素，方法是在應該用於這些索引操作的函式上標註。此外，這些定義是每個型別各自獨有的，任何使用你的型別的程式設計師都可以隱式地使用。

## 概述與摘要 (Overview and Summary)

首先，考慮一個 `Matrix` 型別，使用向量的向量來表示其值。你可以在 `borrow` 和 `borrow_mut` 函式上使用 `index` 語法標註來撰寫一個小型程式庫：

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

現在任何使用此 `Matrix` 型別的人都可以使用索引語法：

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

## 使用方式 (Usage)

如範例所示，如果你定義了一個資料型別和一個相關的索引語法方法，任何人都可以透過在該型別的值上編寫索引語法來叫用該方法：

```move
let mat = matrix::make_matrix(...);
let m_0_0 = mat[0, 0];
```

在編譯期間，編譯器根據運算式的位置和可變性使用情況，將這些轉換為適當的函式叫用：

```move
let mut mat = matrix::make_matrix(...);

let m_0_0 = mat[0, 0];
// 轉換為 `copy matrix::borrow(&mat, 0, 0)`

let m_0_0 = &mat[0, 0];
// 轉換為 `matrix::borrow(&mat, 0, 0)`

let m_0_0 = &mut mat[0, 0];
// 轉換為 `matrix::borrow_mut(&mut mat, 0, 0)`
```

你也可以混合索引運算式與欄位存取：

```move
public struct V { v: vector<u64> }

public struct Vs { vs: vector<V> }

fun borrow_first(input: &Vs): &u64 {
    &input.vs[0].v[0]
    // 轉換為 `vector::borrow(&vector::borrow(&input.vs, 0).v, 0)`
}
````

### 索引函式接受靈活的引數 (Index Functions Take Flexible Arguments)

注意，除了本章節其他部分所述的定義和型別限制外，Move 不會限制索引語法方法作為參數接受的值。這讓你在定義索引語法時實現複雜的程式邏輯，例如一個資料結構，當索引超出範圍時會採用預設值：

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

現在，當你索引到 `MTable` 時，還必須提供預設值：

```move
let string_key: String = ...;
let mut table: MTable<String, u64> = m_table::make_table();
let entry: &mut u64 = &mut table[string_key, 0];
```

這種可延伸的強大功能讓你能為型別編寫精確的索引介面，具體強制執行自訂行為。

## 定義索引語法函式 (Defining Index Syntax Functions)

這個強大的語法形式允許所有使用者定義的資料型別以此方式表現，假設你的定義遵循以下規則：

1. `#[syntax(index)]` 屬性被新增到在主體型別的相同模組中定義的指定函式。
1. 指定的函式具有 `public` 可見性。
1. 函式將參考型別作為主體型別（其第一個引數）並傳回相符的參考型別（如果主體是可變的則為 `mut`）。
1. 每個型別只有一個可變和一個不可變的定義。
1. 不可變和可變版本具有型別協議：
   - 主體型別相符，僅在可變性上不同。
   - 傳回型別與其主體型別的可變性相符。
   - 型別參數（如果存在）在兩個版本間具有相同的限制。
   - 超過主體型別的所有參數都相同。

以下內容和額外範例將詳細描述這些規則。

### 宣告 (Declaration)

若要宣告索引語法方法，在主體型別定義所在的相同模組中，於相關函式定義之上新增 `#[syntax(index)]` 屬性。這向編譯器表示該函式是指定型別的索引存取器。

#### 不可變存取器 (Immutable Accessor)

不可變索引語法方法定義用於唯讀存取。它接收主體型別的不可變參考，並傳回元素型別的不可變參考。在 `std::vector` 中定義的 `borrow` 函式是此的範例：

```move
#[syntax(index)]
public native fun borrow<Element>(v: &vector<Element>, i: u64): &Element;
```

#### 可變存取器 (Mutable Accessor)

可變索引語法方法是不可變存取器的對應物，允許讀取和寫入操作。它接收主體型別的可變參考，並傳回元素型別的可變參考。在 `std::vector` 中定義的 `borrow_mut` 函式是此的範例：

```move
#[syntax(index)]
public native fun borrow_mut<Element>(v: &mut vector<Element>, i: u64): &mut Element;
```

#### 可見性 (Visibility)

為確保索引函式在型別被使用的任何地方都可用，所有索引語法方法都必須具有公開可見性。這確保了在 Move 中跨模組和套件的索引使用都能順利進行。

#### 無重複 (No Duplicates)

除了上述要求外，我們限制每個主體基底型別只能為不可變參考定義一個索引語法方法，為可變參考定義一個索引語法方法。例如，你無法為多型型別定義專門版本：

```move
#[syntax(index)]
public fun borrow_matrix_u64(s: &Matrix<u64>, i: u64, j: u64): &u64 { ... }

#[syntax(index)]
public fun borrow_matrix<T>(s: &Matrix<T>, i: u64, j: u64): &T { ... }
    // 錯誤！Matrix 已經定義了不可變索引語法方法
```

這確保了你總能判斷出正在叫用哪個方法，無需檢查型別實例化。

### 型別限制 (Type Constraints)

預設情況下，索引語法方法有以下型別限制：

**其主體型別（第一個引數）必須是在標記函式相同模組中定義的單一型別的參考。** 這表示你無法為元組、型別參數或值定義索引語法方法：

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

**主體型別必須與傳回型別的可變性相符。** 此限制讓你清楚指定在將索引運算式借用為 `&vec[i]` 和 `&mut vec[i]` 時的預期行為。Move 編譯器使用可變性標記來判斷要呼叫哪種借用形式，以產生適當可變性的參考。因此，我們不允許主體和傳回可變性不同的索引語法方法：

```move
#[syntax(index)]
public fun borrow_imm(x: &mut Matrix<u64>, ...): &u64 { ... }
    // 錯誤！可變性不相容
    // 預期可變參考傳回型別 '&mut'
```

### 型別相容性 (Type Compatibility)

定義不可變和可變索引語法方法對時，它們受到多個相容性限制：

1. 它們必須採用相同數量的型別參數，這些型別參數必須有相同的限制。
1. 型別參數必須按位置而非名稱使用相同。
1. 它們的主體型別除了可變性外必須完全相符。
1. 它們的傳回型別除了可變性外必須完全相符。
1. 所有其他參數型別必須完全相符。

這些限制是為了確保索引語法無論在可變還是不可變位置都表現相同。

為了說明某些錯誤，回想先前的 `Matrix` 定義：

```move
#[syntax(index)]
public fun borrow<T>(s: &Matrix<T>, i: u64, j: u64): &T {
    vector::borrow(vector::borrow(&s.v, i), j)
}
```

以下都是可變版本的型別不相容定義：

```move
#[syntax(index)]
public fun borrow_mut<T: drop>(s: &mut Matrix<T>, i: u64, j: u64): &mut T { ... }
    // 錯誤！`T` 在這裡有 `drop`，在不可變版本中則沒有

#[syntax(index)]
public fun borrow_mut(s: &mut Matrix<u64>, i: u64, j: u64): &mut u64 { ... }
    // 錯誤！這採用不同數量的型別參數

#[syntax(index)]
public fun borrow_mut<T, U>(s: &mut Matrix<U>, i: u64, j: u64): &mut U { ... }
    // 錯誤！這採用不同數量的型別參數

#[syntax(index)]
public fun borrow_mut<U>(s: &mut Matrix<U>, i_j: (u64, u64)): &mut U { ... }
    // 錯誤！這採用不同數量的引數

#[syntax(index)]
public fun borrow_mut<U>(s: &mut Matrix<U>, i: u64, j: u32): &mut U { ... }
    // 錯誤！`j` 是不同的型別
```

再次強調，目標是使不可變和可變版本的使用保持一致。這讓索引語法方法無需根據可變或不可變使用而改變行為或限制，最終確保了一致的程式編寫介面。
