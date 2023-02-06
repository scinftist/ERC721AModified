from sre_constants import SUCCESS
from scripts.helpful_scripts import get_account
from brownie import accounts, config, network, ERC721AToken, ERC721AModifiedToken
from time import sleep
import sys
import random


def deploy_and_create(mint_req=True):
    account = get_account()
    acc = [accounts[0], accounts[1], accounts[2]]
    amm = [50, 20, 20]
    demo = ERC721AModifiedToken.deploy(acc, amm, {"from": account})
    comp = ERC721AToken.deploy(acc, amm, {"from": account})

    print("total Supplies :", demo.totalSupply() == comp.totalSupply())
    num_acc = 10
    minted = [i for i in range(demo.totMinted())]
    # ccc = 200
    add_dict = {}
    for i in range(num_acc):
        add_dict[str(accounts[i])] = "acc-" + str(i)
    # _compGas = 0
    # _deomGas = 0
    verbose = True
    # def compGas(gas):
    #     _compGas = _compGas + gas

    def ad(_ac):
        return add_dict[_ac]

    def tellME(_data):
        Fi = open(
            "./reports/report_Info.txt",
            "a",
        )
        if verbose:
            Fi.write(_data)
        # Close the file
        Fi.close()

    def ch():
        t = 0
        e = 0
        print(len(minted))
        print(demo.totalSupply())
        print(comp.totalSupply())
        for k in range(demo.totalSupply()):

            sleep(0.05)
            t += 1
            i = minted[k]
            # try:
            if demo.ownerOf(i) == comp.ownerOf(i):
                e += 1
            # except:
            else:
                print("prob", i)
                tellME("prob" + str(i))
            if k % 50 == 0:
                print(k)
        print("tot: ", demo.totalSupply())
        print(e, t)

    def trans():
        cas = random.randint(0, 100)
        _compGas = 0
        _deomGas = 0
        if cas < 66:
            # try:
            sup = len(minted)
            rndTok = minted[random.randint(0, sup - 1)]
            print(rndTok)
            own = comp.ownerOf(rndTok)
            otheracc = own
            print(own)
            while own == otheracc:
                otheracc = accounts[random.randint(0, num_acc - 1)]
            tellME(
                "transfer : "
                + str(rndTok)
                + " from: "
                + ad(str(own))
                + " to : "
                + ad(str(otheracc))
                + "\n"
            )
            _compGas = comp.transferFrom(
                own,
                otheracc,
                rndTok,
                {"from": own, "silent": True},
            ).gas_used

            _deomGas = demo.transferFrom(
                own,
                otheracc,
                rndTok,
                {"from": own, "silent": True},
            ).gas_used
            # print(type(tx.gas_used))
            # print(tx.gas_used)
            # sleep(2)
        # except Exception as e:

        #     print("ERRRt")
        #     print(e)
        #     ch()
        #     raise (KeyboardInterrupt)
        else:
            cas = random.randint(0, 100)

            if cas < 90:
                # try:
                sup = len(minted)
                rndTok = minted.pop(random.randint(0, len(minted) - 1))
                print(rndTok)
                own = comp.ownerOf(rndTok)
                tellME("burn : " + str(rndTok) + " from: " + ad(str(own)) + "\n")

                _compGas = comp.burnThis(rndTok, {"from": own}).gas_used
                _deomGas = demo.burnThis(rndTok, {"from": own}).gas_used
            # except Exception as e:
            #     print("ERRRb")
            #     print(e)
            #     print("token ", rndTok)
            #     ch()
            #     raise (KeyboardInterrupt)
            else:
                # try:
                last = demo.totMinted()
                otheracc = accounts[random.randint(0, num_acc - 1)]
                _compGas = comp.multiMint({"from": otheracc}).gas_used
                _deomGas = demo.multiMint({"from": otheracc}).gas_used
                # last = minted[-1]
                # last = demo.totMinted()
                # print(ccc)
                for i in range(10):
                    minted.append(last + i)
                    tellME(
                        "mint token: "
                        + str(last + i)
                        + " to: "
                        + ad(str(otheracc))
                        + " totalSup: "
                        + str(demo.totalSupply())
                        + "\n"
                    )
                # print(minted)
                # sleep(5)

        return _compGas, _deomGas
        # ccc += 5
        # except:
        #     print("ERRR0")
        #     ch()
        #     raise (KeyboardInterrupt)

    # ch()

    # # print(e, t)
    # demo.transferFrom(account, accounts[1], 1, {"from": account})
    # comp.transferFrom(account, accounts[1], 1, {"from": account})

    # comp.transferFrom(accounts[1], accounts[2], 1, {"from": accounts[1]})
    # demo.transferFrom(accounts[1], accounts[2], 1, {"from": accounts[1]})
    # print(99)
    # demo.transferFrom(account, accounts[1], 99, {"from": account})
    # comp.transferFrom(account, accounts[1], 99, {"from": account})

    # demo.transferFrom(accounts[1], accounts[2], 99, {"from": accounts[1]})
    # comp.transferFrom(accounts[1], accounts[2], 99, {"from": accounts[1]})
    # ch()
    d = 0
    c = 0
    for i in range(300):
        _c, _d = trans()
        c += _c
        d += _d
    print(d)
    print(c)
    ch()
    sleep(10)
    return d, c


def main():
    _de = 0
    _ce = 0
    for i in range(2):
        de, ce = deploy_and_create(True)
        _de += de
        _ce += ce
    print(_ce)
    print(_de)
    print(_de / _ce)
