---
description: 'Understand Sui accounts: how they are generated from private keys, identified by addresses, and support multiple crypto schemes.'
---

# 帳戶 (Account)

帳戶是標識用戶的一種方式。帳戶是從私鑰生成的，並透過地址來標識。帳戶可以擁有物件，並可以發送交易。每筆交易都有一個發送者，發送者由[地址](./address)標識。

Sui 支持多種密碼學算法用於生成帳戶。目前支持的兩條曲線是 ed25519、secp256k1，還有一種特殊的生成帳戶方式 —— zklogin。密碼學靈活性（Cryptographic agility）是 Sui 的獨特功能，允許在帳戶生成方面具有靈活性。

## 進一步閱讀

- [Sui 中的密碼學](https://blog.sui.io/wallet-cryptography-specifications/)，載於 [Sui 部落格](https://blog.sui.io)
- [密鑰與地址](https://docs.sui.io/concepts/cryptography/transaction-auth/keys-addresses)，載於 [Sui 官方文件](https://docs.sui.io)
- [簽章](https://docs.sui.io/concepts/cryptography/transaction-auth/signatures)，載於 [Sui 官方文件](https://docs.sui.io)
