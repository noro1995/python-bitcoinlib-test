#!/usr/bin/env python3

# Copyright (C) 2014 The python-bitcoinlib developers
#
# This file is part of python-bitcoinlib.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-bitcoinlib, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

"""Low-level example of how to spend a standard pay-to-pubkey-hash (P2PKH) txout"""

import hashlib

from bitcoin import SelectParams
from bitcoin.core import lx, COIN, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, Hash160
from bitcoin.core.script import CScript, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, SignatureHash, SIGHASH_ALL
from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret


def send(type='testnet', privkey=None, txid=None, address=None, amount=0, vout=0):
    SelectParams(type)

    # Create the (in)famous correct brainwallet secret key.
    # h = hashlib.sha256(b'correct horse battery staple').digest()
    seckey = CBitcoinSecret(privkey)

    # Same as the txid:vout the createrawtransaction RPC call requires
    #
    # lx() takes *little-endian* hex and converts it to bytes; in Bitcoin
    # transaction hashes are shown little-endian rather than the usual big-endian.
    # There's also a corresponding x() convenience function that takes big-endian
    # hex and converts it to bytes.
    txid = lx(txid)
    vout = vout

    # Create the txin structure, which includes the outpoint. The scriptSig
    # defaults to being empty.
    txin = CMutableTxIn(COutPoint(txid, vout))

    # We also need the scriptPubKey of the output we're spending because
    # SignatureHash() replaces the transaction scriptSig's with it.
    #
    # Here we'll create that scriptPubKey from scratch using the pubkey that
    # corresponds to the secret key we generated above.
    txin_scriptPubKey = CScript([OP_DUP, OP_HASH160, Hash160(seckey.pub), OP_EQUALVERIFY, OP_CHECKSIG])

    # Create the txout. This time we create the scriptPubKey from a Bitcoin
    # address.
    txout = CMutableTxOut(0.0003 * COIN, CBitcoinAddress(address).to_scriptPubKey())
    txout2 = CMutableTxOut(0.0002 * COIN, CBitcoinAddress(address).to_scriptPubKey())

    # Create the unsigned transaction.
    tx = CMutableTransaction([txin], [txout, txout2])

    # Calculate the signature hash for that transaction.
    sighash = SignatureHash(txin_scriptPubKey, tx, 0, SIGHASH_ALL)

    # Now sign it. We have to append the type of signature we want to the end, in
    # this case the usual SIGHASH_ALL.
    sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])

    # Set the scriptSig of our transaction input appropriately.
    txin.scriptSig = CScript([sig, seckey.pub])

    # Verify the signature worked. This calls EvalScript() and actually executes
    # the opcodes in the scripts to see if everything worked out. If it doesn't an
    # exception will be raised.
    VerifyScript(txin.scriptSig, txin_scriptPubKey, tx, 0, (SCRIPT_VERIFY_P2SH,))

    # Done! Print the transaction to standard output with the bytes-to-hex
    # function.
    return tx
