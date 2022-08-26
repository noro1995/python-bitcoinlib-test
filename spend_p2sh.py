from bitcoin import SelectParams
from bitcoin.core import b2x, lx, COIN, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, Hash160
from bitcoin.core.script import CScript, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, SignatureHash, SIGHASH_ALL
from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret


def send(seckey, address, txid, amount):
    SelectParams('testnet')

    # Create a redeemScript. Similar to a scriptPubKey the redeemScript must be
    # satisfied for the funds to be spent.
    txin_redeemScript = CScript([seckey.pub, OP_CHECKSIG])
    print('-----------------------')
    print(b2x(txin_redeemScript))

    # Create the magic P2SH scriptPubKey format from that redeemScript. You should
    # look at the CScript.to_p2sh_scriptPubKey() function in bitcoin.core.script to
    # understand what's happening, as well as read BIP16:
    # https://github.com/bitcoin/bips/blob/master/bip-0016.mediawiki
    txin_scriptPubKey = txin_redeemScript.to_p2sh_scriptPubKey()

    # Convert the P2SH scriptPubKey to a base58 Bitcoin address and print it.
    # You'll need to send some funds to it to create a txout to spend.
    txin_p2sh_address = CBitcoinAddress.from_scriptPubKey(txin_scriptPubKey)
    print('-----------------------')
    print('Pay to:', str(txin_p2sh_address))



    # Create the txin structure, which includes the outpoint. The scriptSig
    # defaults to being empty.
    txin = CMutableTxIn(txid)
    print('-----------------------')
    print(txin)
    # Create the txout. This time we create the scriptPubKey from a Bitcoin
    # address.
    txout = CMutableTxOut(amount * COIN, CBitcoinAddress(address).to_scriptPubKey())
    print('-----------------------')
    print(txout)
    # Create the unsigned transaction.
    tx = CMutableTransaction([txin], [txout])

    # Calculate the signature hash for that transaction. Note how the script we use
    # is the redeemScript, not the scriptPubKey. That's because when the CHECKSIG
    # operation happens EvalScript() will be evaluating the redeemScript, so the
    # corresponding SignatureHash() function will use that same script when it
    # replaces the scriptSig in the transaction being hashed with the script being
    # executed.
    sighash = SignatureHash(txin_redeemScript, tx, 0, SIGHASH_ALL)

    # Now sign it. We have to append the type of signature we want to the end, in
    # this case the usual SIGHASH_ALL.
    sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])

    # Set the scriptSig of our transaction input appropriately.
    txin.scriptSig = CScript([sig, txin_redeemScript])

    # Verify the signature worked. This calls EvalScript() and actually executes
    # the opcodes in the scripts to see if everything worked out. If it doesn't an
    # exception will be raised.
    VerifyScript(txin.scriptSig, txin_scriptPubKey, tx, 0, (SCRIPT_VERIFY_P2SH,))
    # Done! Print the transaction to standard output with the bytes-to-hex
    # function.
    return tx
