// ANCHOR: source
/// 模組 `hello_world` 位於具名地址 `hello_world` 下。
/// 具名地址在 `Move.toml` 中設定。
module hello_world::hello_world;

// 從標準程式庫匯入 `String` 類型
use std::string::String;

/// 回傳 "Hello World!" 作為 `String`。
public fun hello_world(): String {
    b"Hello, World!".to_string()
}
// ANCHOR_END: source
