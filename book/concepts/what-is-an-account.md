---
description: 了解 Sui 帳戶 (Sui accounts)：私鑰如何生成帳戶、如何以地址 (address) 識別，以及支援多種加密方案 (crypto schemes)
---

# 帳戶 (Account) {#account}

帳戶是識別使用者的一種方式。帳戶由私鑰產生，並以[地址](./address)識別。帳戶可以擁有物件，也可以發送交易。每筆交易都有一個發送者，發送者由[地址](./address)識別。

帳戶不需要在任何地方建立或註冊：金鑰對一經產生，帳戶即存在，任何有效地址都能在沒有事先設定的情況下接收物件。鏈上並沒有「所有帳戶」的紀錄——一個沒有物件、也沒有交易紀錄的地址，跟一個從未被使用過的地址是無法區分的。

Sui 支援多種帳戶簽章方案：ed25519、ECDSA（基於 secp256k1 與 secp256r1 曲線）、passkeys（基於 WebAuthn 標準的裝置驗證器，例如 Face ID、Touch ID 或硬體安全金鑰）、multisig（由多把金鑰組合控制的帳戶），以及 zkLogin（從 Web2 登入衍生出帳戶）。這種*密碼學靈活性*讓 Sui 在帳戶的建立與控制方式上具備了不尋常的彈性。

## 延伸閱讀 (Further Reading) {#further-reading}

- [Sui 部落格](https://blog.sui.io)中的[〈Sui 密碼學〉](https://blog.sui.io/wallet-cryptography-specifications/)
- [Sui 文件](https://docs.sui.io)中的[〈金鑰與地址〉](https://docs.sui.io/guides/developer/transactions/transaction-auth/auth-overview)
- [Sui 文件](https://docs.sui.io)中的[〈簽章〉](https://docs.sui.io/guides/developer/cryptography/signing)
- [Sui 文件](https://docs.sui.io)中的[〈Passkey〉](https://docs.sui.io/develop/cryptography/passkeys)
