# 向量 (Vector)

`vector<T>` 是 Move 中唯一的可變長度集合類型。它可以儲存任意類型的元素 `T`。

## 基本語法

### 字面量 (Literals)

```move
let v1 = vector[1, 2, 3];
let v2 = vector<u8>[10, 20];
let empty_vec = vector[];
```

### 字串字面量 (String Literals)

Move 支援字節字串 (Byte Strings) 和十六進制字串 (Hex Strings)，它們的類型都是 `vector<u8>`。

- `b"Hello!"`: 字節字串。
- `x"48656C6C6F21"`: 十六進制字串。

## 操作 (Operations)

透過 `std::vector` 模組提供支援：

- `empty<T>()`: 建立空向量。
- `singleton<T>(t)`: 建立長度為 1 的向量。
- `push_back<T>(&mut v, t)`: 在末尾新增元素。
- `pop_back<T>(&mut v)`: 移除並返回最後一個元素。
- `borrow<T>(&v, i)`: 不可變借用。
- `borrow_mut<T>(&mut v, i)`: 可變借用。
- `destroy_empty<T>(v)`: 銷毀空向量。
- `length<T>(&v)`: 返回長度。
- `contains<T>(&v, &e)`: 檢查是否包含某個元素。

## 銷毀與複製

- **銷毀**: 如果元素類型沒有 `drop` 能力，則不能隱式捨棄，必須使用 `vector::destroy_empty`（且向量必須為空）。
- **複製**: 只有當元素類型 `T` 具有 `copy` 能力時，`vector<T>` 才能被複製。

## 所有權 (Ownership)

`vector` 的行為遵循其包含元素的所有權規則。
