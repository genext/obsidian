---
title: "블록체인(Blockchain)"
created: 2024-03-09 15:16:19
updated: 2025-09-29 13:04:03
---
## 용어 정리
    * Bitcoin 수량
      * 2100만 개로 한정.
      * 2140년에 발행 완료.
    * block
      * 매 10분마다 새로 블록을 생성하도록 2주마다 블록체인 네트웍에서 계산하고 그 결과에 따라 difficulty를 조정.
      * 블록체인의 무결성을 유지하기 위해 블록을 추가할  때 
        * 블록의 구성정보(거래내역) 검증과 
        * 추가 조건(작업 증명, 지분 증명)이 필요.
      * 구성정보
        * block hash
          * block data + previous block hash -> hash 생성
        * previous block hash
        * block data
          * 거래내역
      * Block Height #memo ^SFyC2YAiu
        * the sequential number of a block within the blockchain.
      * Oracle
		블록체인과 실세계를 잇는 가교 역할
	    * 블록체인 외부 데이터를 스마트계약에 전달
    	* 실세계에서 어떤 일이 발생 시 스마트계약 실행하도록 설정 가능
    	* 반대로 블록체인에서 특정 거래가 이루어지면 오러클을 호출해 실세계에 어떤 일을 하도록 전달 가능.
The first block (genesis block) has height 0.
`Fork resolution`: In case of competing chains, the chain with the greater height typically becomes the canonical one
`Synchronization`: New nodes use block height to catch up with the network
`Protocol upgrades`: Many blockchain updates activate at specific block heights
Think of block height like page numbers in a book - it gives you an exact reference point in the blockchain's chronological history.
    * Blockchain Node's local storage #memo ^am2NHpDZ_
      * bitcoin: custom DB
### PBM
## Purpose Bound Money
## ERC(Ethereum Request for Comments) 표준
### - 토큰 표준
- 토큰 생성하는 것을 mint(<-> burn)라고 함. ethereum과 달리 채굴되는 것이 아님.
- ERC-20 - fungible token
- ERC-721 - non fungible token
- ERC-1155 - NFT + FT 
	-  거래 효율성, 편의 증가
	* 잘못 보낸 토큰 회수 가능
	* mint/burn 허용하지 않음(?)
- 토큰 비교
	![[100. media/image/Z_ebz3KiCV.png]]
- ERC-7291 PBM
        * [x] https://eips.ethereum.org/EIPS/eip-7291
ethereum: levelDB(key/value)
`The actual data within LevelDB is structured as a Merkle Patricia Trie (MPT). This specialized data structure efficiently stores and updates the Ethereum's "world state," which includes account balances, contract code, and contract storage.`

      * nomadcoin: go's key/value DB, "bolt". No more version up. → bolt가 data race에서 버그가 있어서 나중에 b-bolt도 바꿈.
    * mining(commission + Bitcoin)
      * 목적: 블록체인을 유지하고 새 블록을 추가하는 노력이 의미 있는 노력이다.
      * 블록체인에 들어오는 데이터(거래내역)를 검증(?). -> 첫 번째 보상(commission)(?)
      * 검증된 거래내역 모은 candidate 블록에 필요한 hash 값은?(puzzle)
      * hash값 구하면 블록 채굴
      * 블록체인에 전송. --> coinbase transaction 생김 -> 두 번째 보상 Bitcoin 생성 -> miner는 이 Bitcoin 획득!!
      * 하지만 consensus(51%)까지 받아야 블록체인에 완전히 올라갈 수 있음.
    * transaction ^8ovx_gFJ1
      * Bitcoin's UTXO(Unspent Transaction Output) model #memo  ^QzmhvOtlR
        * ![[100. media/image/TUcbz0WzaE.png]]

Bitcoin's accounting system where coins exist as discrete "chunks" (UTXOs) that must be spent entirely. Transactions consume old UTXOs as inputs and create new UTXOs as outputs. Like physical coins - you can't spend half a coin, only give the whole coin and get change back.

Key Point: No account balances - just unspent transaction outputs that get consumed and recreated.
      * Ethereum's Account-based model #memo ^6XXp6egtf
        * ****Core Concept****: Ethereum uses accounts with persistent balances, like traditional bank accounts, rather than Bitcoin's UTXO system.
Transactions directly modify account balances - when Alice sends ETH to Bob, her balance decreases and his increases, with no separate "coins" being created or destroyed.
****Key advantages**** for Ethereum:
- Supports smart contracts that need persistent state
- Simpler for developers (familiar banking-like model)
- Enables complex applications like DeFi and NFTs
- Works better with Ethereum's gas fee system
This model was chosen specifically to support Ethereum's goal of being ****a programmable blockchain platform**** rather than just a digital currency.
      * coinbase transaction과 Mempool에 있는 거래내역이 한 블록으로 저장
        * 채굴
          * 입력: coinbase transaction: 블록체인 네트웍이  채굴자에게 보상하는 거래/bitcoin 돈 찍어내기
          * 출력: 채굴자 잔액
        * Mempool: 블록에 저장되기 전, 거래 내역이 있는 곳. 수수료(gas)를 내야 여기서 블록으로 옮겨준다.
          * 이용자간 거래 생성 및 저장
        * confirm transactions: Mempool -> block
      * 거래 검증
        * 거래 시도자가 코인을 소유하고 있다는 것을 증명해야 하는데, Tx의 TxIn은 이전 거래의 TxOut으로 만들어졌으므로 이를 이용해서 검증
        * 현 transaction ID는 거래내역(Tx)을 hash한 것.
        * signature는 TxIn에 들어가는 지갑 소유자의 private key로 transaction ID를 서명한 값.
        * 거래 검증은 현 거래의 signature가 대상인데 먼저 TxIn에 있는 transaction ID를 가진 TxOut을 찾아서 거기 있는 hash of the address(지갑소유자의 공개키)로 검증.
      * AI assistant (Claude Sonnet 4): Transaction Overview and Types
        * A **transaction** is a discrete unit of work or exchange that involves the transfer of value, information, or resources between parties. Transactions are fundamental to commerce, finance, and database systems.
        * ## Key Characteristics
          * **Atomicity**: The transaction either completes entirely or fails completely
          * **Consistency**: Maintains system integrity before and after execution  
          * **Isolation**: Concurrent transactions don't interfere with each other
          * **Durability**: Once committed, changes are permanent
        * ## Common Types
          * 1. **Financial Transactions**
            * Bank transfers and payments
            * Credit/debit card purchases  
            * Investment trades
            * Currency exchanges
          * 2. **Database Transactions**
            * Data insertion, updates, or deletions
            * Batch processing operations
            * Backup and recovery procedures
          * 3. **Business Transactions**
            * Sales and purchases
            * Contract agreements
            * Service deliveries
            * Supply chain operations
          * 4. **Digital Transactions**
            * Online payments
            * Cryptocurrency transfers
            * Digital asset exchanges
            * API calls and data exchanges
        * ## Transaction Lifecycle
          * 1. **Initiation**: Transaction request is made
          * 2. **Validation**: System checks authorization and availability
          * 3. **Processing**: Core transaction logic executes
          * 4. **Confirmation**: Results are verified and recorded
          * 5. **Settlement**: Final state is established and communicated
        * Transactions form the backbone of modern economic and technological systems, ensuring reliable and accountable exchanges across various domains.
    * balance
      * UXTO model in bitcoin
        * ![[100. media/image/qaBuOOJ4J6.png]]
        * Bitcoin's accounting system where coins exist as discrete "chunks" (UTXOs) that must be spent entirely. Transactions consume old UTXOs as inputs and create new UTXOs as outputs. Like physical coins - you can't spend half a coin, only give the whole coin and get change back.
        * Key Point: No account balances - just unspent transaction outputs that get consumed and recreated.
      * 특정인의 잔액은 결국 블록체인의 모든 거래 내역을 뒤진 후 계산하는 수밖에 없을 것 같네...DB에 따로 해당인의 잔액 자체를 저장하지 않는다면...
        * 잔액 조회가 빈번한 텐데 그럼 결국 블록체인 전체 거래내역 cache가 꼭 필요할 것이다.
        * 은행 계좌 잔액과 블록체인 잔액을 연동할 때 이 둘 값이 안 맞으면? 매일 밤에 잔액 대조?
    * Bitcoin 반감기
      * 4년 마다 블록 하나 올릴 때마다 생성되는 Bitcoin 수가 반으로 줄어듦. 50 -> 25 -> 12.5 -> 6.25
      * [[March 9th, 2024]] 현재(19:21) 6.25개로 올 5월에 반감기.

    * p2p
    * consensus algorithm
      * 거래내역, 블록을 검증하기 위한 방법
      * 답을 찾기는 아주 어렵게 하지만 답을 검증하기는 아주 쉽게.(숫자 0이 difficulty 숫자만큼 시작하는 hash값 구하는 것이 답 찾기가 어렵지만 검증은 0의 갯수만 세면 되기 때문에 쉽다.)
      * 블록에 있는 데이터가 참인지 합의에 이르기 위한 방법. 네트웍 보호하기 위한 메커니즘.
      * proof of work
        * miner가 puzzle (전체 네트웍크가 아는 질문)을 풀면 블록 생성되고 이를 인정받으면 Bitcoin 받음.
          * 난이도(difficulty)가 높을 수록 어려워짐.
          * 난이도(difficulty)가 3이고 블록데이터(block data + prevHash)로 hash를 돌렸을 때 0 세 개로 시작하는 hash값을 얻으려면 nonce는 몇?
            * 2022년에는 0이 19개로 시작하는 해쉬를 구해야 한다고...
          * miner는 nonce를 바꾸면서 위 hash 구함.
          * nonce를 맞추면 블록 생성됨.
          * consensus 51% 받으면 블록체인에 완전히 올라감.
      * proof of stake
        * 3세대 블록체인(Etherium 2.0)에서 사용. 1세대는 Bitcoin, 2세대는 Etherium 
    * 전자지갑
      * Bitcoin 등은 네트웍에만 존재. 그럼 내 소유권은 어떻게 주장?
        * 땅 사고 파는 것과 비슷. 땅은 소유자에게 직접 넘겨지는 것이 아니고 땅문서에 있는 소유자가 바뀜.
      * 암호화(asymmetric encryption)한 구분값이 Encrypted wallet.
        * asymmetric encryption/decryption
          * 내 비공개 키를 일단 만들고 그것으로 공개 키(자물쇠) 생성
          * 공개 키를 공유할 수 있음.
          * 중요한 데이터를 보낼 때 상대방 공개 키로 내 데이터를 암호화.
            * 상대방은 자신의 비공개 키로 암호를 풀어 내 공개 키와 데이터를 얻음.
          * 상대방은 응답을 다시 내 공개키로 암호화하고 전송
            * 나는 반대로 내 비공개 키로 암호를 푼다.
        * 공개키가 **내 지갑 주소**가 된다.
        * 지갑 생성하는 것은 내 비공개 키 만드는 것.
        * 이후 내 공개 키로 암호화한 것을 내 비공개 키로만 열 수 있음.
      * Ethereum wallet? #memo ^i99IaSMys
        * **EOA**(Externally Owned Account), one of two main types of accounts in Ethereum (the other being **Contract Accounts**).
          * Controlled by private key: holds the private key.
          * Can initiate transactions: EOAs are the only type of account that can start transactions on their own. They can send ETH, interact with smart contracts, or deploy new contracts.
          * No code: they're just accounts that hold a balance and can send transactions.
          * Address format: EOA addresses look like regular Ethereum addresses (e.g., 0x742d35Cc6634C0532925a3b8D3Ac3d76...) and are derived from the public key.
    * smart contract
      * 이더리움 등에서 solidity 언어로 코딩해서 블록 형태로 올라감. 누구나 사용 가능.
      * 클래스 구조
      * 거래에 필요한 코드를 작성해서 블록체인 네트웍에 올리는 것. --> 중개인이 필요 없어짐.
      * 2024년 현재 etherium이 가장 큰 smart contract 플랫폼. NFT, DEX 등..
      * 단점
        * trustless 네트웍 환경을 요구한다. 원래 블록체인 네트워크는 그 속성 덕분에 trustless인데 smart contract와 연결되는 되는 세상이 블록체인 외부라면 trustless가 깨진다. 
          * 이 문제를 해결하기 위해서 trustful 세계와 trustless 블록체인 네트웍을 중간에서 연결하는 blockchain oracle이 있다고 함.
      * EVM(Etherium Virtual Machin)
        * smart contract runtime environment.
      * gas
        * smart contract 실행에 필요한 수수료로 EVM이 부과
    * NFT
      * Token
        * token을 만들기 위해서 2가지 기능이 있는 smart contract 만듦.
          * 돈을 받으면
          * token 보내준다.
      * Non Fungible Token
        * 토큰 단 한 개만 발행하는 smart contract 만든다.
        * 그 토큰 안에 무엇이든 저장 가능. 사진, 동영상, 파일 등.. 
    * stable coin
      * 암호 화폐이면서 smart contract 가능.
      * USD와 1:1로 교환 가능. 회사가 보증.
      * USDT, USDC, BUSD(binance)
    * DEX
      * Decentralized exchange <-> Binance, bitsum(centralized)
    * 51% attack
      * 거짓 블록에 대한 consensus가 51%를 넘기도록 네트웍 참여자를 설득해서 블록체인 장악.
      * 현재 Bitcoin 노드 수는 7만 개 이상
      * 결국 computing power가 49%를 제압하는 정도로 엄청나면 단 한 대로도 51% consensus 가능.
      * hard fork로 방어 가능.
        * 블록체인 네트웍을 새로 만들어서 기존 것과 다르게 운영.
    * Blockchain trilemma
      * scalability, decentralization, security 세 개를 모두 만족하는 cryptocurrency가 없다.
    * ATN(All That Node)
      * 블록체인을 위한 개발 인프라 제공 목적으로 나온 회사.
      * 무료 API key를 받아서 여러 블록체인에 연결해서 개발 가능?
    * Zero knowledge proof

    * DiFi(Decentralized Financial)
      * [ ] AAVE 주목
## 특징
    * Decentralized -> 모든 노드가 블록체인의 전체 복사본 보관?
    * append만 가능. 그럼 사용할수록 블록체인이 커지는 문제는 어떻게 해결할까? 블록체인을 자식을 만드나?
    * 속도 느림. 1초에 거래 5개만 처리. 이더리움은 30개 처리. 에너지 많이 잡아먹음.
      * Etherium 2.0은 이를 개선한 것. 1초 당 거래를 25,000 ~ 100,000, 에너지 소모를 99% 줄임.
## 암호 화폐 종류
    * 사업 중심
      * Cosmos
        * 상호운용성 중심. 즉 블록체인의 인터넷이 되려고 함.
        * 블록체인을 만들 수 있는 프레임워크
          * Cosmos.sdk(Go)를 이용해서 모듈을 조립해서 블록체인 생성 가능. 그 다음 cosmos hub에 연결해서 cosmos hub가 제공하는 보안을 누리고 다른 블록체인과 네트워킹할 수 있음.
          * BNB(Binance coin), Terra가  이렇게 만들어짐.
      * Polkadot
        * Rust 기반 블록체인 프레임워크
    * 이더리움과 경쟁
      * blockchain trillema를 해결했다고 주장.
      * Cardano
        * Haskell
          * more like mathematics than just a programming language
        * aim to Decentralized Financial System for global world.
        * verified by peer review of a paper and apply the new idea.
      * Algorand
        * sdk in Rust, etc
        * 창시자가 Zero knowledge proof 발표
      * Solana
        * smart contract in Rust, C++
        * transaction cost is very low but before there was a crash for 6h -> maybe not stable yet.
        * Proof of history
## nomad typescript blockchain 강의 정리
    * nodeJS package crypto library 문제
      * 해시값 구할 때 crypto 라이브러리 사용하지만 아래 처럼 import하면 에러 표시
```typescript
import crypto from "crypto"   

--> 에러 메시지
Module "crypto" has no default export.
```
      * 해결방법
        * import * as crypto from "crypto" 로 하거나 또는,
        * import 문은 그대로 두고 tsconfig.json 수정해서 esModuleInterop를 true로 설정
```json
{
    "include": [ "src" ],
    "compilerOptions": {
        "outDir": "build",
        "target": "ES6",
        "lib": ["ES6"],
        "strict": true,
        "esModuleInterop": true,
        "module": "CommonJS"
    }
}
```
        * 그래도 type declaration을 못 찾는다는 패키지가 있다. 이유는 해당 라이브러리는 타입스크립트로 작성된 것이 아니어서 .d.ts 파일을 못 찾아서 나오는 문제.
          * DefinitelyTyped라는 Git repository가 있는데 npm의 거의 모든 package에 대한 타입 정의를 갖고 있음.
          * .d.ts 설치
            * node.js package에 대한 모든 .d.ts 설치
```shell
npm i -D @types/node
```
          * 최근 npm은 package 설치할 때 알아서 .d.ts까지 같이 설치.
    * source zip
      * ![[100. media/archives/tKRJpPvQUl.zip]]
## singapore blockchain
    * blockchain, every industry
    * GeTS
      * Global eTrade Services
        * OTB
          * Open Trade Blockchain
    * adoption of blockchain technology in Singapore
## sol 파일 정적 분석, 동적 분석프로그램:  [[October 31st, 2024#^LxF4qVRAq|스마트계약 sol 파일 분석 프로그램 및 결과]]
## 참고자료
    * https://homoefficio.github.io/2016/01/23/BlockChain-%EA%B8%B0%EC%B4%88-%EA%B0%9C%EB%85%90/
    * https://homoefficio.github.io/2017/11/19/%EB%B8%94%EB%A1%9D%EC%B2%B4%EC%9D%B8-%ED%95%9C-%EB%B2%88%EC%97%90-%EC%9D%B4%ED%95%B4%ED%95%98%EA%B8%B0/index.html?fbclid=IwY2xjawNG3RBleHRuA2FlbQIxMABicmlkETFDaFFjOVFpRDZBTTBFQXIwAR6gg9sNvrXTqsaR7cvbPJybuCxhmsOctyZhrn6JD_1pDi9Vz_ETl7XuSHzarQ_aem_D1b4f4qU_oyJnvMQCZNyqw