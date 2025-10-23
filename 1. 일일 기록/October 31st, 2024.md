---
title: "October 31st, 2024"
created: 2024-10-31 07:55:16
updated: 2024-10-31 07:57:06
---
07:24 출근
## 스마트계약 sol 파일 분석 프로그램 및 결과
```
	  const { expect } = require("chai");
const { ContractFactory } = require("ethers");
const { anyValue } = require("@nomicfoundation/hardhat-chai-matchers/withArgs");
const { loadFixture, time } = require("@nomicfoundation/hardhat-network-helpers");
const { abi: tdAbi, bytecode: tdBytecode } = require('../example/TD_factory');
const { abi: veAbi, bytecode: veBytecode } = require('../example/MockVe_factory');

const contractName = process.env.CONTRACT_NAME;

describe(`${contractName}::`, function () {
    const zeroAddress = "0x0000000000000000000000000000000000000000";
    const maxUint256 = "115792089237316195423570985008687907853269984665640564039457584007913129639935";

    let fixtures, pbmContract, tdContract, veTxContract;
    let deployer, manager, creator, payer, payee;

    async function makeUnixExpiry(years) {
        const oneYearInMs = 365 * 24 * 60 * 60 * 1000;
        const hundredYearsLater = Date.now() + (years * oneYearInMs);
        const unixTimestamp = Math.floor(hundredYearsLater / 1000);
        return unixTimestamp.toString();
    }

    async function deployContractsEx() {
        const [deployer, manager, creator, payer, payee, ...signers] = await ethers.getSigners();

        // Deploy TD
        const tdFactory = new ContractFactory(tdAbi, tdBytecode, deployer);
        const tdContract = await tdFactory.connect(deployer).deploy();
        await tdContract.waitForDeployment();

        // Deploy VeTx
        const veFactory = new ContractFactory(veAbi, veBytecode, deployer);
        const veContract = await veFactory.connect(deployer).deploy();
        await veContract.waitForDeployment();

        // Deploy PBMWrapperEx (ì€í–‰ê°„ ì „ì†¡ ì§€ì›)
        const partId = "000";
        const voAddress = zeroAddress;
        const expiry = await makeUnixExpiry(100);
        const voucherId = "bank1-vc-id";

        const pbmFactory = (await ethers.getContractFactory(contractName));
        const pbmContract = await pbmFactory.connect(deployer).deploy(
            deployer.address,
            manager.address,
            partId,
            expiry,
            voAddress,
            voucherId);
        await pbmContract.waitForDeployment();

        const [adminRole, managerRole, minterRole, pauserRole] = await Promise.all([
            pbmContract.DEFAULT_ADMIN_ROLE(),
            pbmContract.MANAGER_ROLE(),
            pbmContract.MINTER_ROLE(),
            pbmContract.PAUSER_ROLE(),
        ]);

        return {
            pbmContract,
            tdContract,
            veContract,
            signers: {
                deployer,
                manager,
                creator,
                payer,
                payee,
                others: signers,
            },
            roles: {
                adminRole,
                managerRole,
                minterRole,
                pauserRole,
            },
        };
    }

    beforeEach(async function () {
        // ìŠ¤ë§ˆíŠ¸ê³„ì•½ ì„¤ì¹˜
        fixtures = await loadFixture(deployContractsEx);
        pbmContract = fixtures.pbmContract;
        tdContract = fixtures.tdContract;
        veTxContract = fixtures.veContract;

        deployer = fixtures.signers.deployer;
        manager = fixtures.signers.manager;
        creator = fixtures.signers.creator;
        payer = fixtures.signers.payer;
        payee = fixtures.signers.payee;

        // set TD for test
        const tdFund = ethers.parseUnits("10000000", await tdContract.decimals());
        const mintTx1 = await tdContract.connect(deployer).mint(deployer.address, tdFund);
        await mintTx1.wait();
        const mintTx2 = await tdContract.connect(deployer).mint(manager.address, tdFund);
        await mintTx2.wait();
        const mintTx3 = await tdContract.connect(deployer).mint(payer.address, tdFund);
        await mintTx3.wait();
        const mintTx4 = await tdContract.connect(deployer).mint(payee.address, tdFund);
        await mintTx4.wait();
        const mintTx5 = await tdContract.connect(deployer).mint(creator.address, tdFund);
        await mintTx5.wait();


        // initialise2 by ì°¸ê°€ê¸°ê´€ ê´€ë¦¬ìž
        const creatorAddress = creator.address;
        const initialise2Tx = await pbmContract
            .connect(manager)
            .initialise2(
                creatorAddress,
                await tdContract.getAddress(),
                await veTxContract.getAddress()
            );
        await initialise2Tx.wait();

        // PBM í† í° ìƒì„±
        const tokenName = "cashback";
        const unitAmount = "1";
        const tokenExpiry = await  makeUnixExpiry(10);
        const uri = "https://voucher.bank.co.kr";
        const voucherType = "1";
        const cashbackRate ="100";
        const oneTimeMaxSpending = "0";
        const tx = await pbmContract
            .connect(manager)
            .createPBMTokenType(tokenName, unitAmount, tokenExpiry, uri, voucherType, cashbackRate, oneTimeMaxSpending);
        const receipt = await tx.wait();

        // ì˜ë¢°ê¸°ê´€ì´ ì°¸ê°€ê¸°ê´€ì—ê²Œ ë°°í¬ ê¶Œí•œ ìœ„ìž„
        const setApproveAllTx = await pbmContract.connect(creator).setApprovalForAll(manager.address, true);
        await setApproveAllTx.wait();

        // ì‚¬ìš©ì²˜ ì¶”ê°€
        const addMerchantTx = await pbmContract.connect(manager).addMerchantAddresses([payee.address], "");
        await addMerchantTx.wait();

        // ì˜ë¢°ê¸°ê´€ TDë¥¼ ì‚¬ìš© ìŠ¹ì¸
        const approveTxs = await Promise.all([
            tdContract.connect(creator).approve(await pbmContract.getAddress(), maxUint256)
        ]);

        await Promise.all(approveTxs.map((tx) => tx.wait()));
    });

    // You can nest describe calls to create subsections.
    describe("DEFAULT_ADMIN_ROLE()::", function () {
        it("DEFAULT_ADMIN_ROLEì´ ë°˜ë“œì‹œ ì¡´ìž¬í•´ì•¼ í•¨", async function () {
            await pbmContract.DEFAULT_ADMIN_ROLE();
        });
    });

    describe("MANAGER_ROLE()::", function () {
        it("MANAGER_ROLEì´ ë°˜ë“œì‹œ ì¡´ìž¬í•´ì•¼ í•¨", async function () {
            await pbmContract.MANAGER_ROLE();
        });
    });

    describe("PAUSER_ROLE()::", function () {
        it("PAUSER_ROLEì´ ë°˜ë“œì‹œ ì¡´ìž¬í•´ì•¼ í•¨", async function () {
            await pbmContract.PAUSER_ROLE();
        });
    });

    describe("MINTER_ROLE()::", function () {
        it("MINTER_ROLEì´ ë°˜ë“œì‹œ ì¡´ìž¬í•´ì•¼ í•¨", async function () {
            await pbmContract.MINTER_ROLE();
        });
    });

    describe("REVOKE_ROLE()::", function () {
        it("REVOKE_ROLEì´ ë°˜ë“œì‹œ ì¡´ìž¬í•´ì•¼ í•¨", async function () {
            await pbmContract.REVOKE_ROLE();
        });
    });

    describe("UPGRADER_ROLE()::", function () {
        it("UPGRADER_ROLEì´ ë°˜ë“œì‹œ ì¡´ìž¬í•´ì•¼ í•¨", async function () {
            await pbmContract.UPGRADER_ROLE();
        });
    });

    describe("initialise1(address,address,string,uint256,address,string)::", function () {
        it("defaultAdminì€ DEFAULT_ADMIN_ROLE ì„ ë¶€ì—¬ë°›ì•„ì•¼ í•¨", async function () {
            const isAdmin = await pbmContract.hasRole(fixtures.roles.adminRole, deployer.address);
            expect(isAdmin).to.be.true;
        });
    });

    describe("grantRole(bytes32,address)::", function () {
        it("DEFAULT_ADMIN_ROLEì€ grantRoleì„ í˜¸ì¶œí•  ìˆ˜ ìžˆìŒ", async function() {
            const user = fixtures.signers.others[0];
            await pbmContract.connect(deployer).grantRole(fixtures.roles.managerRole, user.address);
            expect(await pbmContract.hasRole(fixtures.roles.managerRole, user.address)).to.be.true;
        })

        it("MANAGER_ROLEì€ grantRoleì„ í˜¸ì¶œí•  ìˆ˜ ìžˆìŒ", async function() {
            const user = fixtures.signers.others[0];
            await pbmContract.connect(manager).grantRole(fixtures.roles.managerRole, user.address);
            expect(await pbmContract.hasRole(fixtures.roles.managerRole, user.address)).to.be.true;
        })

        it("ì´ ì™¸ì˜ í˜¸ì¶œìžëŠ” grantRoleì„ í˜¸ì¶œí•  ìˆ˜ ì—†ìŒ", async function() {
            const user = fixtures.signers.others[0];
            await expect(pbmContract.connect(user).grantRole(fixtures.roles.managerRole, user.address)).to.be.reverted;
        })
    })

    describe("revokeRole(bytes32,address)::", function () {
        beforeEach(async function () {
            const user = fixtures.signers.others[0];
            const managerRole = fixtures.roles.managerRole;
            await pbmContract.connect(deployer).grantRole(managerRole, user.address);
        })

        it("DEFAULT_ADMIN_ROLEì€ revokeRoleì„ í˜¸ì¶œí•  ìˆ˜ ìžˆìŒ", async function() {
            const user = fixtures.signers.others[0];
            const managerRole = fixtures.roles.managerRole;
            await pbmContract.connect(deployer).revokeRole(fixtures.roles.managerRole, user.address);
            expect(await pbmContract.hasRole(managerRole, user.address)).to.be.false;
        })

        it("MANAGER_ROLEì€ revokeRoleì„ í˜¸ì¶œí•  ìˆ˜ ìžˆìŒ", async function() {
            const user = fixtures.signers.others[0];
            const managerRole = fixtures.roles.managerRole;
            await pbmContract.connect(manager).revokeRole(managerRole, user.address);
            expect(await pbmContract.hasRole(managerRole, user.address)).to.be.false;
        })

        it("ì´ ì™¸ì˜ í˜¸ì¶œìžëŠ” revokeRoleì„ í˜¸ì¶œí•  ìˆ˜ ì—†ìŒ", async function() {
            const user = fixtures.signers.others[0];
            const managerRole = fixtures.roles.managerRole;
            await expect(pbmContract.connect(user).revokeRole(managerRole, user.address)).to.be.reverted;
        })
    })

    describe("getInitInfo()::", function () {
        it("initialialise1, inititialise2ì—ì„œ ìž…ë ¥ëœ ê°’ë“¤ì´ ì˜¬ë°”ë¥´ê²Œ ë°˜í™˜ë˜ì–´ì•¼ í•¨", async function() {
            const voAddress = ethers.Wallet.createRandom();
            const veTxAddress = ethers.Wallet.createRandom();
            const tdAddress = await tdContract.getAddress();

            const pbmFactory_t = (await ethers.getContractFactory(contractName));
            const pbmContract_t = await pbmFactory_t.connect(deployer).deploy(
                deployer.address,
                manager.address,
                "partId",
                "1000000",
                voAddress,
                "voucherId");
            await pbmContract_t.waitForDeployment();

            const initialise2Tx = await pbmContract_t
                .connect(manager)
                .initialise2(
                    creator.address,
                    tdAddress,
                    veTxAddress
                );
            await initialise2Tx.wait();

            const initInfo = await  pbmContract_t.getInitInfo();

            expect(initInfo[0]).to.eq("partId");
            expect(initInfo[1]).to.eq(manager.address);
            expect(initInfo[2]).to.eq(creator.address);
            expect(initInfo[3]).to.eq(tdAddress);
            expect(initInfo[4]).to.eq(voAddress);
            expect(initInfo[5]).to.eq(veTxAddress);
            expect(initInfo[6]).to.eq("voucherId");
        })
    })

    describe("blacklistPayerAddresses(address[],string)::", function () {
        it("blacklistPayerAddresses í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ accounts ì— í•´ë‹¹í•˜ëŠ” ì£¼ì†Œë“¤ì— ëŒ€í•´ì„œ isPayerBlacklisted() í˜¸ì¶œ ê°’ì´ true ì—¬ì•¼ í•¨", async function () {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            expect(await pbmContract.isPayerBlacklisted(user1)).to.equal(false);
            expect(await pbmContract.isPayerBlacklisted(user2)).to.equal(false);
            expect(await pbmContract.isPayerBlacklisted(user3)).to.equal(false);

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).blacklistPayerAddresses(userList, "");

            expect(await pbmContract.isPayerBlacklisted(user1)).to.equal(true);
            expect(await pbmContract.isPayerBlacklisted(user2)).to.equal(true);
            expect(await pbmContract.isPayerBlacklisted(user3)).to.equal(true);
        });

        it("PayerBlacklist ì´ë²¤íŠ¸ê°€ add íƒœê·¸ë¡œ ë°œìƒí•´ì•¼ í•¨", async function () {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            const tx = await pbmContract.connect(manager).blacklistPayerAddresses(userList, "");

            await expect(tx)
                .to.emit(pbmContract, "PayerBlacklist")
                .withArgs("add", userList, anyValue);
        });
    });

    describe("unBlacklistPayerAddresses(address[],string)::", function () {
        beforeEach(async function() {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).blacklistPayerAddresses(userList, "");

            expect(await pbmContract.isPayerBlacklisted(user1)).to.equal(true);
            expect(await pbmContract.isPayerBlacklisted(user2)).to.equal(true);
            expect(await pbmContract.isPayerBlacklisted(user3)).to.equal(true);
        })

        it("unBlacklistPayerAddresses í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ accounts ì— í•´ë‹¹í•˜ëŠ” ì£¼ì†Œë“¤ì— ëŒ€í•´ì„œ isPayerBlacklisted() í˜¸ì¶œ ê°’ì´ false ì—¬ì•¼ í•¨", async function () {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).unBlacklistPayerAddresses(userList, "");

            expect(await pbmContract.isPayerBlacklisted(user1)).to.equal(false);
            expect(await pbmContract.isPayerBlacklisted(user2)).to.equal(false);
            expect(await pbmContract.isPayerBlacklisted(user3)).to.equal(false);
        });

        it("PayerBlacklist ì´ë²¤íŠ¸ê°€ remove íƒœê·¸ë¡œ ë°œìƒí•´ì•¼ í•¨", async function () {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            const tx = await pbmContract.connect(manager).unBlacklistPayerAddresses(userList, "");

            await expect(tx)
                .to.emit(pbmContract, "PayerBlacklist")
                .withArgs("remove", userList, anyValue);
        });
    });

    describe("blacklistAddresses(address[],string)::", function () {
        it("blacklistAddresses í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ accounts ì— í•´ë‹¹í•˜ëŠ” ì£¼ì†Œë“¤ì— ëŒ€í•´ì„œ isBlacklisted() í˜¸ì¶œ ê°’ì´ true ì—¬ì•¼ í•¨", async function () {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            expect(await pbmContract.isBlacklisted(user1)).to.equal(false);
            expect(await pbmContract.isBlacklisted(user2)).to.equal(false);
            expect(await pbmContract.isBlacklisted(user3)).to.equal(false);

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).blacklistAddresses(userList, "");

            expect(await pbmContract.isBlacklisted(user1)).to.equal(true);
            expect(await pbmContract.isBlacklisted(user2)).to.equal(true);
            expect(await pbmContract.isBlacklisted(user3)).to.equal(true);
        });

        it("Blacklist ì´ë²¤íŠ¸ê°€ add íƒœê·¸ë¡œ ë°œìƒí•´ì•¼ í•¨", async function () {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            const tx = await pbmContract.connect(manager).blacklistAddresses(userList, "");

            await expect(tx)
                .to.emit(pbmContract, "Blacklist")
                .withArgs("add", userList, anyValue);
        });
    });

    describe("unBlacklistAddresses(address[],string)::", function () {
        beforeEach(async function() {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).blacklistAddresses(userList, "");

            expect(await pbmContract.isBlacklisted(user1)).to.equal(true);
            expect(await pbmContract.isBlacklisted(user2)).to.equal(true);
            expect(await pbmContract.isBlacklisted(user3)).to.equal(true);
        })

        it("unBlacklistAddresses í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ accounts ì— í•´ë‹¹í•˜ëŠ” ì£¼ì†Œë“¤ì— ëŒ€í•´ì„œ isBlacklisted() í˜¸ì¶œ ê°’ì´ false ì—¬ì•¼ í•¨", async function () {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).unBlacklistAddresses(userList, "");

            expect(await pbmContract.isBlacklisted(user1)).to.equal(false);
            expect(await pbmContract.isBlacklisted(user2)).to.equal(false);
            expect(await pbmContract.isBlacklisted(user3)).to.equal(false);
        });

        it("Blacklist ì´ë²¤íŠ¸ê°€ remove íƒœê·¸ë¡œ ë°œìƒí•´ì•¼ í•¨", async function () {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            const tx = await pbmContract.connect(manager).unBlacklistAddresses(userList, "");

            await expect(tx)
                .to.emit(pbmContract, "Blacklist")
                .withArgs("remove", userList, anyValue);
        });
    });

    describe("addMerchantAddresses(address[],string)::", function () {
        it("addMerchantAddresses í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ accounts ì— í•´ë‹¹í•˜ëŠ” ì£¼ì†Œë“¤ì— ëŒ€í•´ì„œ isMerchant() í˜¸ì¶œ ê°’ì´ true ì—¬ì•¼ í•¨", async function () {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            expect(await pbmContract.isMerchant(user1)).to.equal(false);
            expect(await pbmContract.isMerchant(user2)).to.equal(false);
            expect(await pbmContract.isMerchant(user3)).to.equal(false);

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).addMerchantAddresses(userList, "");

            expect(await pbmContract.isMerchant(user1)).to.equal(true);
            expect(await pbmContract.isMerchant(user2)).to.equal(true);
            expect(await pbmContract.isMerchant(user3)).to.equal(true);
        });

        it("MerchantList ì´ë²¤íŠ¸ê°€ add íƒœê·¸ë¡œ ë°œìƒí•´ì•¼ í•¨", async function () {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            const tx = await pbmContract.connect(manager).addMerchantAddresses(userList, "");

            await expect(tx)
                .to.emit(pbmContract, "MerchantList")
                .withArgs("add", userList, anyValue);
        });
    });

    describe("removeMerchantAddresses(address[],string)::", function () {
        beforeEach(async function() {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).addMerchantAddresses(userList, "");

            expect(await pbmContract.isMerchant(user1)).to.equal(true);
            expect(await pbmContract.isMerchant(user2)).to.equal(true);
            expect(await pbmContract.isMerchant(user3)).to.equal(true);
        })

        it("removeMerchantAddresses í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ accounts ì— í•´ë‹¹í•˜ëŠ” ì£¼ì†Œë“¤ì— ëŒ€í•´ì„œ isMerchant() í˜¸ì¶œ ê°’ì´ false ì—¬ì•¼ í•¨", async function () {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).removeMerchantAddresses(userList, "");

            expect(await pbmContract.isMerchant(user1)).to.equal(false);
            expect(await pbmContract.isMerchant(user2)).to.equal(false);
            expect(await pbmContract.isMerchant(user3)).to.equal(false);
        });

        it("MerchantList ì´ë²¤íŠ¸ê°€ remove íƒœê·¸ë¡œ ë°œìƒí•´ì•¼ í•¨", async function () {
            const user1 = fixtures.signers.others[0];
            const user2 = fixtures.signers.others[1];
            const user3 = fixtures.signers.others[2];
            const userList = [user1.address, user2.address, user3.address];

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            const tx = await pbmContract.connect(manager).removeMerchantAddresses(userList, "");

            await expect(tx)
                .to.emit(pbmContract, "MerchantList")
                .withArgs("remove", userList, anyValue);
        });
    });

    describe("mint(uint256,uint256,address)::", function () {
        it("receiverê°€ blacklistì¸ ê²½ìš° revert ë˜ì–´ì•¼ í•¨", async function() {
            const tokenId = "0";
            const amount = "5000";
            const user = fixtures.signers.others[0];

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).blacklistAddresses([user], "");
            await expect(pbmContract.connect(manager).mint(tokenId, amount, user)).to.be.reverted;
        })

        it("receiverê°€ zero addressì¸ ê²½ìš° revert ë˜ì–´ì•¼ í•¨", async function() {
            const tokenId = "0";
            const amount = "5000";

            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await expect(pbmContract.connect(manager).mint(tokenId, amount, zeroAddress)).to.be.reverted;
        })

        describe("", function () {
            beforeEach(async function () {
                this.user = fixtures.signers.others[0];
                this.tokenId = "0";
                this.amount = "5000";
                this.pbmAddress = await pbmContract.getAddress();

                expect(await tdContract.balanceOf(this.pbmAddress)).to.eq("0");
                expect(await pbmContract.balanceOf(this.user.address, this.tokenId)).to.eq("0");
                expect(await pbmContract.getTokenCount(this.tokenId)).to.eq("0");

                this.tx = await pbmContract.connect(manager).mint(this.tokenId, this.amount, this.user.address)
            })

            it("mint í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ tokenIdì˜ PBM ë°”ìš°ì²˜ì— ëŒ€í•´ amount ë§Œí¼ receiver balanceê°€ ì¦ê°€í•´ì•¼ í•¨", async function() {
                expect(await pbmContract.balanceOf(this.user.address, this.tokenId)).to.eq(this.amount);
            })

            it("mint í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ tokenIdì˜ ì‚¬ìš© ê°€ëŠ¥í•œ ìˆ˜ëŸ‰(balanceSupply)ì´ amounts ë§Œí¼ ì¦ê°€í•´ì•¼ í•¨", async function() {
                expect(await  pbmContract.getTokenCount(this.tokenId)).to.eq(this.amount);
            })

            it("í˜¸ì¶œ ê²°ê³¼ PBMWrapper êµ¬í˜„ì²´ì˜ digitalMoney balanceê°€ amount * (PBMTokenManager.getTokenValue(tokenId) ë§Œí¼ ì¦ê°€í•´ì•¼ í•¨", async function() {
                const tokenValue = await pbmContract.getTokenValue(this.tokenId);

                expect(await tdContract.balanceOf(await  pbmContract.getAddress()))
                    .to.deep.eq(BigInt(this.amount) * BigInt(tokenValue));
            })

            it("TokenWrap ì´ë²¤íŠ¸ê°€ ë°œìƒí•´ì•¼ í•¨", async function() {
                await expect(this.tx)
                    .to.emit(pbmContract, "TokenWrap")
                    .withArgs(anyValue, [this.tokenId], [this.amount], anyValue, anyValue);
            })

            it("TransferSingle ì´ë²¤íŠ¸ê°€ ë°œìƒí•´ì•¼ í•¨", async function() {
                await expect(this.tx)
                    .to.emit(pbmContract, "TransferSingle")
                    .withArgs(manager.address, zeroAddress, this.user.address, this.tokenId, this.amount);
            })
        })
    })

    describe("batchMint(uint256[],uint256[],address)::", function () {
        beforeEach("", async function() {
            this.tokenIds = ["0", "1", "2"];
            this.amounts = ["5000", "10000", "15000"];
            this.user = fixtures.signers.others[0];

            // PBM í† í° ìƒì„±
            const tokenExpiry = await makeUnixExpiry(10);
            const uri = "https://voucher.bank.co.kr";
            const voucherType = "1";
            const cashbackRate ="100";
            const oneTimeMaxSpending = "0";

            const tokenTx1 = await pbmContract
                .connect(manager)
                .createPBMTokenType("tokenId-1", "10", tokenExpiry, uri, voucherType, cashbackRate, oneTimeMaxSpending);
            await tokenTx1.wait();

            const tokenTx2 = await pbmContract
                .connect(manager)
                .createPBMTokenType("tokenId-1", "100", tokenExpiry, uri, voucherType, cashbackRate, oneTimeMaxSpending);
            await tokenTx2.wait();
        })

        it("receiverê°€ blacklistì¸ ê²½ìš° revert ë˜ì–´ì•¼ í•¨", async function() {
            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            this.tx = await pbmContract.connect(manager).blacklistAddresses([this.user.address], "");
            await expect(pbmContract.connect(manager).batchMint(this.tokenIds, this.amounts, this.user.address)).to.be.reverted;
        })

        it("receiverê°€ zero addressì¸ ê²½ìš° revert ë˜ì–´ì•¼ í•¨", async function() {
            await expect(pbmContract.connect(manager).batchMint(this.tokenIds, this.amounts, zeroAddress)).to.be.reverted;
        })

        describe("", function () {
            beforeEach(async function () {
                this.tx = await pbmContract
                    .connect(manager)
                    .batchMint(
                        this.tokenIds,
                        this.amounts,
                        this.user.address
                    );
            })

            it("mint í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ tokenIdì˜ PBM ë°”ìš°ì²˜ì— ëŒ€í•´ amount ë§Œí¼ receiver balanceê°€ ì¦ê°€í•´ì•¼ í•¨", async function() {
                expect(await pbmContract.balanceOfBatch(
                        [this.user.address, this.user.address, this.user.address],
                        this.tokenIds
                    )
                ).to.deep.eq(this.amounts);
            })

            it("mint í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ tokenIdì˜ ì‚¬ìš© ê°€ëŠ¥í•œ ìˆ˜ëŸ‰(balanceSupply)ì´ amounts ë§Œí¼ ì¦ê°€í•´ì•¼ í•¨", async function() {
                expect(await pbmContract.getTokenCount(this.tokenIds[0])).to.eq(this.amounts[0]);
                expect(await pbmContract.getTokenCount(this.tokenIds[1])).to.eq(this.amounts[1]);
                expect(await pbmContract.getTokenCount(this.tokenIds[2])).to.eq(this.amounts[2]);
            })

            it("í˜¸ì¶œ ê²°ê³¼ PBMWrapper êµ¬í˜„ì²´ì˜ digitalMoney balanceê°€ amount * (PBMTokenManager.getTokenValue(tokenId) ë§Œí¼ ì¦ê°€í•´ì•¼ í•¨", async function() {
                const tokenValues = await Promise.all(
                    this.tokenIds.map(async (tokenId) => {
                        return await pbmContract.getTokenValue(tokenId);
                    })
                );

                const expectedBal = this.amounts.reduce(
                    (acc, amount, i) => acc + BigInt(amount) * BigInt(tokenValues[i]), BigInt("0")
                );

                expect(await tdContract.balanceOf(await  pbmContract.getAddress()))
                    .to.deep.eq(expectedBal);
            })

            it("TokenWrap ì´ë²¤íŠ¸ê°€ ë°œìƒí•´ì•¼ í•¨", async function() {
                await expect(this.tx)
                    .to.emit(pbmContract, "TokenWrap")
                    .withArgs(anyValue, this.tokenIds, this.amounts, anyValue, anyValue);
            })

            it("TransferBatch ì´ë²¤íŠ¸ê°€ ë°œìƒí•´ì•¼ í•¨", async function() {
                await expect(this.tx)
                    .to.emit(pbmContract, "TransferBatch")
                    .withArgs(manager.address, zeroAddress, this.user.address, this.tokenIds, this.amounts);
            })
        })
    })

    describe("safeTransferFrom(address,address,uint256,uint256,bytes)::", function () {
        beforeEach(async function () {
            // pbm ì œì¡°
            this.tokenId = "0";
            this.mintAmount = "1000000";
            this.user = fixtures.signers.others[0];

            const mintTx = await pbmContract
                .connect(manager)
                .mint(this.tokenId, this.mintAmount, manager.address);
            await mintTx.wait();
        });

        it("amount ê°’ì€ fromì´ ì†Œìœ í•˜ê³  ìžˆëŠ” balanceë³´ë‹¤ í´ ìˆ˜ ì—†ìŒ", async function() {
            const amount = await pbmContract.balanceOf(manager.address, this.tokenId) + BigInt("1");

            await expect(
                pbmContract
                    .connect(manager)
                    .safeTransferFrom(
                        manager.address,
                        this.user.address,
                        this.tokenId,
                        amount,
                        "0x"
                    )
            ).to.be.reverted;
        })

        it("fromì´ payer blacklistì— í¬í•¨ë˜ì–´ ìžˆë‹¤ë©´ revert ë˜ì–´ì•¼ í•¨", async function() {
            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).blacklistPayerAddresses([manager.address], "");

            await expect(
                pbmContract
                    .connect(manager)
                    .safeTransferFrom(
                        manager.address,
                        this.user.address,
                        this.tokenId,
                        this.mintAmount,
                        "0x"
                    )
            ).to.be.reverted;
        })

        it("toê°€ blacklistì— í¬í•¨ë˜ì–´ ìžˆë‹¤ë©´ revert ë˜ì–´ì•¼ í•¨", async function() {
            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).blacklistAddresses([this.user.address], "");

            await expect(
                pbmContract
                    .connect(manager)
                    .safeTransferFrom(
                        manager.address,
                        this.user.address,
                        this.tokenId,
                        this.mintAmount,
                        "0x"
                    )
            ).to.be.reverted;
        })

        it("ë‹¨ì¼ PBM ë°”ìš°ì²˜ê°€ ì´ë™í•˜ëŠ” ê²½ìš°, TransferSingle ì´ë²¤íŠ¸ê°€ ë°œìƒí•´ì•¼ í•¨", async function() {
            const tx = await pbmContract
                .connect(manager)
                .safeTransferFrom(
                    manager.address,
                    this.user.address,
                    this.tokenId,
                    this.mintAmount,
                    "0x"
                )

            await expect(tx)
                .to.emit(pbmContract, "TransferSingle")
                .withArgs(manager.address, manager.address, this.user.address, this.tokenId, this.mintAmount);
        })
    })

    describe("safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)::", function () {
        beforeEach(async function () {
            this.tokenIds = ["0", "1", "2"];
            this.amounts = ["5000", "10000", "15000"];
            this.user = fixtures.signers.others[0];

            // PBM í† í° ì œì¡°
            const tokenExpiry = await makeUnixExpiry(10);
            const uri = "https://voucher.bank.co.kr";
            const voucherType = "1";
            const cashbackRate ="100";
            const oneTimeMaxSpending = "0";

            const tokenTx1 = await pbmContract
                .connect(manager)
                .createPBMTokenType("tokenId-1", "10", tokenExpiry, uri, voucherType, cashbackRate, oneTimeMaxSpending);
            await tokenTx1.wait();

            const tokenTx2 = await pbmContract
                .connect(manager)
                .createPBMTokenType("tokenId-1", "100", tokenExpiry, uri, voucherType, cashbackRate, oneTimeMaxSpending);
            await tokenTx2.wait();

            const mintTx = await pbmContract
                .connect(manager)
                .batchMint(
                    this.tokenIds,
                    this.amounts,
                    manager.address
                );
            await mintTx.wait();
        });

        it("amount ê°’ì€ fromì´ ì†Œìœ í•˜ê³  ìžˆëŠ” balanceë³´ë‹¤ í´ ìˆ˜ ì—†ìŒ", async function() {
            const amount0 = await pbmContract.balanceOf(manager.address, this.tokenIds[0]) + BigInt("1");
            const amount1 = await pbmContract.balanceOf(manager.address, this.tokenIds[1]) + BigInt("1");
            const amount2 = await pbmContract.balanceOf(manager.address, this.tokenIds[2]) + BigInt("1");
            const amounts = [amount0, amount1, amount2];

            await expect(
                pbmContract
                    .connect(manager)
                    .safeBatchTransferFrom(
                        manager.address,
                        this.user.address,
                        this.tokenIds,
                        amounts,
                        "0x"
                    )
            ).to.be.reverted;
        })

        it("fromì´ payer blacklistì— í¬í•¨ë˜ì–´ ìžˆë‹¤ë©´ revert ë˜ì–´ì•¼ í•¨", async function() {
            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).blacklistAddresses([this.user.address], "");

            await expect(
                pbmContract
                    .connect(manager)
                    .safeBatchTransferFrom(
                        manager.address,
                        this.user.address,
                        this.tokenIds,
                        this.amounts,
                        "0x"
                    )
            ).to.be.reverted;
        })

        it("toê°€ blacklistì— í¬í•¨ë˜ì–´ ìžˆë‹¤ë©´ revert ë˜ì–´ì•¼ í•¨", async function() {
            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).blacklistAddresses([this.user.address], "");

            await expect(
                pbmContract
                    .connect(manager)
                    .safeBatchTransferFrom(
                        manager.address,
                        this.user.address,
                        this.tokenIds,
                        this.amounts,
                        "0x"
                    )
            ).to.be.reverted;
        })

        it("ë‹¤ì¤‘ PBM ë°”ìš°ì²˜ê°€ ì´ë™í•˜ëŠ” ê²½ìš°, TransferBatch ì´ë²¤íŠ¸ê°€ ë°œìƒí•´ì•¼ í•¨", async function() {
            const tx = await pbmContract
                .connect(manager)
                .safeBatchTransferFrom(
                    manager.address,
                    this.user.address,
                    this.tokenIds,
                    this.amounts,
                    "0x"
                )

            await expect(tx)
                .to.emit(pbmContract, "TransferBatch")
                .withArgs(manager.address, manager.address, this.user.address, this.tokenIds, this.amounts);
        })
    })

    describe("revokePBM(uint256)::", function () {
        beforeEach(async function () {
            // pbm ì œì¡°
            this.tokenId = "0";
            this.mintAmount = "1000000";
            this.user = fixtures.signers.others[0];

            const mintTx = await pbmContract
                .connect(manager)
                .mint(this.tokenId, this.mintAmount, manager.address);
            await mintTx.wait();
        })

        it("revokePBM í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ tokenIdì˜ ì‚¬ìš© ê°€ëŠ¥í•œ ìˆ˜ëŸ‰(balanceSupply)ì— ìƒì‘í•˜ëŠ” PBMWrapper êµ¬í˜„ì²´ì˜ digitalMoney balanceê°€ getPBMRevokeValue(tokenId) ë§Œí¼ ê°ì†Œí•´ì•¼ í•¨", async function () {
            const revokeBal = await  pbmContract.getPBMRevokeValue(this.tokenId);
            const beforeBal = await tdContract.balanceOf(await  pbmContract.getAddress());
            (await pbmContract.connect(manager).revokePBM(this.tokenId)).wait();
            const afterBal = await tdContract.balanceOf(await  pbmContract.getAddress());

            expect(beforeBal - afterBal).to.eq(revokeBal);
        });

        it("revokePBM í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ tokenIdì— ëŒ€í•´ì„œ ì‚¬ìš© ê°€ëŠ¥í•œ ìˆ˜ëŸ‰(balanceSupply)ì´ 0ê°œ ë˜ì–´ì•¼ í•¨", async function () {
            expect(await pbmContract.getTokenCount(this.tokenId)).to.not.eq(0);
            (await pbmContract.connect(manager).revokePBM(this.tokenId)).wait();
            expect(await pbmContract.getTokenCount(this.tokenId)).to.eq(0);
        });

        it("revokePBMì„ í†µí•´ PBM ë°”ìš°ì²˜ê°€ í™˜ìˆ˜ë  ì‹œ PBMrevokeWithdraw eventê°€ ë°œìƒí•´ì•¼ í•¨", async function () {
            const tokenId = "0";
            const tx = await pbmContract.connect(manager).revokePBM(tokenId);

            await expect(tx)
                .to.emit(pbmContract, "PBMrevokeWithdraw")
                .withArgs(creator.address, tokenId, anyValue, anyValue);
        });
    });

    describe("refundPBM(address,uint256[],uint256[])::", function () {
        beforeEach(async function () {
            this.tokenIds = ["0", "1", "2"];
            this.amounts = ["5000", "10000", "15000"];
            this.user = fixtures.signers.others[0];

            // PBM í† í° ì œì¡°
            const tokenExpiry = await makeUnixExpiry(10);
            const uri = "https://voucher.bank.co.kr";
            const voucherType = "1";
            const cashbackRate ="100";
            const oneTimeMaxSpending = "0";

            const tokenTx1 = await pbmContract
                .connect(manager)
                .createPBMTokenType("tokenId-1", "10", tokenExpiry, uri, voucherType, cashbackRate, oneTimeMaxSpending);
            await tokenTx1.wait();

            const tokenTx2 = await pbmContract
                .connect(manager)
                .createPBMTokenType("tokenId-1", "100", tokenExpiry, uri, voucherType, cashbackRate, oneTimeMaxSpending);
            await tokenTx2.wait();
        });

        it("toê°€ blacklistì— í¬í•¨ë˜ì–´ ìžˆë‹¤ë©´ revert ë˜ì–´ì•¼ í•¨", async function () {
            // ê¶Œí•œ ì„¤ì •ì´ ì§„í–‰ë  ìˆ˜ ìžˆìœ¼ë¯€ë¡œ, manager roleì„ ì´ìš©í•´ í•¨ìˆ˜ í˜¸ì¶œ ì§„í–‰
            await pbmContract.connect(manager).blacklistAddresses([this.user.address], "");

            await expect(
                veTxContract
                    .refundPBM(
                        await pbmContract.getAddress(),
                        this.user.address,
                        this.tokenIds,
                        this.amounts
                    )
            ).to.be.reverted;
        });

        it("refundPBM í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ amounts ì— í•´ë‹¹í•˜ëŠ” ë§Œí¼ toì˜ tokenIds balanceê°€ ì¦ê°€í•´ì•¼ í•¨", async function () {
            const beforeBals = await pbmContract.balanceOfBatch(
                [this.user.address, this.user.address, this.user.address],
                this.tokenIds
            );

            (await veTxContract
                .refundPBM(
                    await pbmContract.getAddress(),
                    this.user.address,
                    this.tokenIds,
                    this.amounts
                )
            ).wait();

            const afterBals = await pbmContract.balanceOfBatch(
                [this.user.address, this.user.address, this.user.address],
                this.tokenIds
            );

            expect(afterBals[0] - beforeBals[0]).to.eq(this.amounts[0]);
            expect(afterBals[1] - beforeBals[1]).to.eq(this.amounts[1]);
            expect(afterBals[2] - beforeBals[2]).to.eq(this.amounts[2]);
        });

        it("refundPBM í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ tokenIdsì˜ ì‚¬ìš© ê°€ëŠ¥í•œ ìˆ˜ëŸ‰(balanceSupply)ì´ amounts ë§Œí¼ ì¦ê°€ë˜ì–´ì•¼ í•¨", async function () {
            const beforeSupplies = await Promise.all((this.tokenIds).map(id => pbmContract.getTokenCount(id)));

            (await veTxContract
                    .refundPBM(
                        await pbmContract.getAddress(),
                        this.user.address,
                        this.tokenIds,
                        this.amounts
                    )
            ).wait();

            const afterSupplies = await Promise.all((this.tokenIds).map(id => pbmContract.getTokenCount(id)));
            expect(afterSupplies[0] - beforeSupplies[0]).to.be.equal(this.amounts[0]);
            expect(afterSupplies[1] - beforeSupplies[1]).to.be.equal(this.amounts[1]);
            expect(afterSupplies[2] - beforeSupplies[2]).to.be.equal(this.amounts[2]);
        });

        it("TokenWrapForRefund eventê°€ ë°œìƒí•´ì•¼ í•¨", async function () {
            const refundTx = await veTxContract
                    .refundPBM(
                        await pbmContract.getAddress(),
                        this.user.address,
                        this.tokenIds,
                        this.amounts
                    );

            await expect(refundTx).to.emit(pbmContract, "TokenWrapForRefund");
        });
    });

    describe("setApprovalForAll(address,bool)::", function () {
        it("setApprovalForAll í•¨ìˆ˜ë¥¼ trueë¡œ í˜¸ì¶œí•œ ê²°ê³¼ isApprovedForAll()ì˜ í˜¸ì¶œ ê°’ì´ trueê°€ ë˜ì–´ì•¼ í•¨", async function () {
            const holder = fixtures.signers.others[0];
            const proxy = fixtures.signers.others[1];

            expect(await pbmContract.isApprovedForAll(holder.address, proxy.address)).to.be.false;
            await pbmContract.connect(holder).setApprovalForAll(proxy.address, true);
            expect(await pbmContract.isApprovedForAll(holder.address, proxy.address)).to.be.true;
        });

        it("setApprovalForAll í˜¸ì¶œ ì‹œ ApprovalForAll ì´ë²¤íŠ¸ê°€ ë°œìƒí•´ì•¼ í•¨", async function () {
            const holder = fixtures.signers.others[0];
            const proxy = fixtures.signers.others[1];

            await expect(pbmContract.connect(holder).setApprovalForAll(proxy.address, true))
                .to.emit(pbmContract, 'ApprovalForAll')
                .withArgs(holder.address, proxy.address, true);
        });

        it("setApprovalForAll í•¨ìˆ˜ë¥¼ false í˜¸ì¶œí•œ ê²°ê³¼ isApprovedForAll()ì˜ í˜¸ì¶œ ê°’ì´ falseê°€ ë˜ì–´ì•¼ í•¨", async function () {
            const holder = fixtures.signers.others[0];
            const proxy = fixtures.signers.others[1];

            expect(await pbmContract.isApprovedForAll(holder.address, proxy.address)).to.be.false;
            await pbmContract.connect(holder).setApprovalForAll(proxy.address, true);
            expect(await pbmContract.isApprovedForAll(holder.address, proxy.address)).to.be.true;
            await pbmContract.connect(holder).setApprovalForAll(proxy.address, false);
            expect(await pbmContract.isApprovedForAll(holder.address, proxy.address)).to.be.false;
        });

        it("Zero Addressë¥¼ ëŒ€ìƒìœ¼ë¡œ setApprovalForAll í•¨ìˆ˜ë¥¼ í˜¸ì¶œí•˜ë©´ revert ë˜ì–´ì•¼ í•¨", async function () {
            const holder = fixtures.signers.others[0];
            await expect(pbmContract.connect(holder).setApprovalForAll(zeroAddress, true)).to.be.reverted;
        });

    });

    describe("pause()::", function () {
        it("pause í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼, paused()ì˜ í˜¸ì¶œ ê°’ì´ trueë¡œ ë°˜í™˜ë˜ì–´ì•¼ í•¨", async function () {
            await pbmContract.connect(deployer).grantRole(fixtures.roles.pauserRole, deployer);

            expect(await pbmContract.paused()).to.be.false;
            await pbmContract.connect(deployer).pause();
            expect(await pbmContract.paused()).to.be.true;
        });
    });

    describe("unpause()::", function () {
        it("unpause í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼, paused()ì˜ í˜¸ì¶œ ê°’ì´ falseë¡œ ë°˜í™˜ë˜ì–´ì•¼ í•¨", async function () {
            await pbmContract.connect(deployer).grantRole(fixtures.roles.pauserRole, deployer);

            expect(await pbmContract.paused()).to.be.false;
            await pbmContract.connect(deployer).pause();
            expect(await pbmContract.paused()).to.be.true;
            await  pbmContract.connect(deployer).unpause();
            expect(await pbmContract.paused()).to.be.false;
        });
    });

    describe("getCashback(uint256,address,uint256)::", function () {
        it("getCashback í•¨ìˆ˜ê°€ ì¡´ìž¬í•´ì•¼ í•¨", async function () {
            await pbmContract.getCashback("0", manager.address, "1");
        });
    });

    describe("getSubsidy(uint256,address,uint256)::", function () {
        it("getSubsidy í•¨ìˆ˜ê°€ ì¡´ìž¬í•´ì•¼ í•¨", async function () {
            await pbmContract.getCashback("0", manager.address, "1");
        });
    });

    describe("areTokensValid(uint256[])::", function () {
        it("í˜¸ì¶œ ê²°ê³¼ ë§Œë£Œëœ tokenIds ì— ëŒ€í•´ì„œëŠ” `false` ë¥¼ ë°˜í™˜í•´ì•¼ í•¨", async function () {
            const name = "tokenId-1"
            const unitAmount = "10";
            const tokenExpiry = await makeUnixExpiry(1);
            const uri = "https://voucher.bank.co.kr";
            const voucherType = "1";
            const cashbackRate ="100";
            const oneTimeMaxSpending = "0";
            const tokenId = "1"; // expected token id

            const tokenTx = await pbmContract
                .connect(manager)
                .createPBMTokenType(
                    name,
                    unitAmount,
                    tokenExpiry,
                    uri,
                    voucherType,
                    cashbackRate,
                    oneTimeMaxSpending
                );
            await tokenTx.wait();

            await time.increaseTo(BigInt(tokenExpiry) + BigInt("1"));

            expect(await pbmContract.areTokensValid(["1"])).to.be.false;
        });
    });


    describe("", function () {
        beforeEach(async  function () {
            // PBM í† í° ìƒì„±
            this.name = "tokenId-1"
            this.unitAmount = "10";
            this.tokenExpiry = await makeUnixExpiry(10);
            this.uri = "https://voucher.bank.co.kr";
            this.voucherType = "1";
            this.cashbackRate ="100";
            this.oneTimeMaxSpending = "0";
            this.tokenId = "1"; // expected token id

            const tokenTx = await pbmContract
                .connect(manager)
                .createPBMTokenType(
                    this.name,
                    this.unitAmount,
                    this.tokenExpiry,
                    this.uri,
                    this.voucherType,
                    this.cashbackRate,
                    this.oneTimeMaxSpending
                );
            await tokenTx.wait();

            // PBM í† í° ë¯¼íŒ…
            this.user = fixtures.signers.others[0];
            this.tokenAmount = "10000"

            const mintTx = await pbmContract.connect(manager).mint(this.tokenId, this.tokenAmount, this.user);
            await mintTx.wait();
        })

        it("getTokenCreator(uint256):: getTokenCreator í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ `tokenTypes[tokenId].creator` ë¥¼ ë°˜í™˜í•´ì•¼ í•¨", async function () {
            expect(await pbmContract.getTokenCreator(this.tokenId)).to.eq(manager.address);
        });

        it("getTokenDetails(uint256):: getTokenDetails í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ í•´ë‹¹ ë°”ìš°ì²˜ì˜ name, amount, expiry, creatorë¥¼ ì˜¬ë°”ë¥´ê²Œ ë°˜í™˜í•´ì•¼ í•¨", async function () {
            const tokenDetails = await  pbmContract.getTokenDetails(this.tokenId);

            expect(tokenDetails[0]).to.eq(this.name);
            expect(tokenDetails[1]).to.eq(this.unitAmount);
            expect(tokenDetails[2]).to.eq(this.tokenExpiry);
            expect(tokenDetails[3]).to.eq(manager.address);
        });

        it("setTokenExpiry(uint256,uint256):: setTokenExpiry í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ `tokenExpiry`ê°€ ì•Œë§žê²Œ ë³€ê²½ë˜ì–´ì•¼ í•¨", async function () {
            const targetExpiry = this.tokenExpiry + BigInt(1);
            await pbmContract.connect(manager).setTokenExpiry(this.tokenId, targetExpiry);
            expect((await pbmContract.getTokenDetails(this.tokenId))[2]).to.eq(targetExpiry);
        });

        it("setVoucherPolicy(uint256,uint256,uint256,uint256):: setVoucherPolicy í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ í•´ë‹¹ ë°”ìš°ì²˜ì— ëŒ€í•œ ì •ì±… ì‚¬í•­ì´ ì•Œë§žê²Œ ë³€ê²½ë˜ì–´ì•¼ í•¨", async function () {
            const tokenExpiry = await makeUnixExpiry(100);
            const cashbackRate = "200";
            const oneTimeMaxSpending = "10";

            await pbmContract.connect(manager).setVoucherPolicy(this.tokenId, tokenExpiry, cashbackRate, oneTimeMaxSpending);
            const voucherPolicy = await  pbmContract.getVoucherPolicy(this.tokenId);

            expect(voucherPolicy[0]).to.deep.eq(tokenExpiry);
            expect(voucherPolicy[2]).to.deep.eq(cashbackRate);
            expect(voucherPolicy[3]).to.deep.eq(oneTimeMaxSpending);
        });

        it("getTokenValue(uint256):: getTokenValue í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ `tokenTypes[tokenId].amount` ë¥¼ ë°˜í™˜í•´ì•¼ í•¨", async function () {
            const value = await  pbmContract.getTokenValue(this.tokenId);
            expect(value).to.eq(this.unitAmount);
        });

        it("getTokenCount(uint256):: getTokenCount í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ `tokenTypes[tokenId].balanceSupply` ë¥¼ ë°˜í™˜í•´ì•¼ í•¨", async function () {
            const count = await  pbmContract.getTokenCount(this.tokenId);
            expect(count).to.eq(this.tokenAmount);
        });

        it("getPBMRevokeValue(uint256):: getPBMRevokeValue í•¨ìˆ˜ í˜¸ì¶œ ê²°ê³¼ `tokenTypes[tokenId].amount * tokenTypes[tokenId].balanceSupply` ë¥¼ ë°˜í™˜í•´ì•¼ í•¨", async function () {
            const value = await  pbmContract.getTokenValue(this.tokenId);
            const count = await  pbmContract.getTokenCount(this.tokenId);
            const revokeValue = await  pbmContract.getPBMRevokeValue(this.tokenId);

            expect(revokeValue).to.eq(value * count);
        });
    });
}); // EOT: PBMWrapperEx í…ŒìŠ¤íŠ¸
```
결과
![[100. media/documents/IRcBWwRtBt.pdf]]