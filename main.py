from bitcoin import SelectParams
from bitcoin.rpc import Proxy
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret
from bitcoin.core import lx, b2x
from spend_p2pkh import send

SelectParams('testnet')
proxy = Proxy(
    service_url='http://admin:123456@127.0.0.1:18332/wallet/ongrid',
    service_port=18332
)

def main():
    tx = run()
    print(b2x(tx.serialize()))
    # res = proxy.sendrawtransaction(tx)
    # print(res)
def run():
    unspents = proxy.listunspent()
    for unspent in unspents:
        print(unspent)
        unspent_address = unspent['address']
        privkey = proxy.dumpprivkey(unspent_address)
        txout = unspent['outpoint']
        res = send(
            privkey='cRvbKVSRUfTrCkYkmtW8aLs8r9Vd5RDMK4EUGvVzWm8AVbvC34cD',
            txid='6d072c9ff040f25e39aa47b9f36b1cfb92a07cdc1723b81ae118763a98118f5a',
            amount=0.00059990,
            address='mfdxeTYJBwvgR9o9CoV89RuGGPi8BJACjD',
            vout=1

        )
        return res

if __name__ == '__main__':
    main()