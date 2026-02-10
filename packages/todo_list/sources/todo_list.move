// ANCHOR: all
/// 模組：todo_list
module todo_list::todo_list;

use std::string::String;

/// 待辦事項清單。可由所有者管理並與他人分享。
public struct TodoList has key, store {
    id: UID,
    items: vector<String>
}

/// 建立新的待辦事項清單。
public fun new(ctx: &mut TxContext): TodoList {
    let list = TodoList {
        id: object::new(ctx),
        items: vector[]
    };

    (list)
}

/// 將新的待辦事項新增至清單。
public fun add(list: &mut TodoList, item: String) {
    list.items.push_back(item);
}

/// 依索引從清單中移除待辦事項。
public fun remove(list: &mut TodoList, index: u64): String {
    list.items.remove(index)
}

/// 刪除清單及管理它的能力。
public fun delete(list: TodoList) {
    let TodoList { id, items: _ } = list;
    id.delete();
}

/// 取得清單中的項目數量。
public fun length(list: &TodoList): u64 {
    list.items.length()
}
// ANCHOR_END: all
