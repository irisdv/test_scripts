import asyncio
import os
from dotenv import load_dotenv
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call

load_dotenv()

node_url = os.getenv(f"RPC_URL")
client = FullNodeClient(node_url=node_url)
chain = StarknetChainId.TESTNET

account_address = os.getenv(f"ACCOUNT_ADDRESS")
priv_key = os.getenv(f"PRIVATE_KEY")

basicAlphabet = "abcdefghijklmnopqrstuvwxyz0123456789-"
bigAlphabet = "这来"
small_size_plus = len(basicAlphabet) + 1
big_size_plus = len(bigAlphabet) + 1


def extract_stars(str):
    k = 0
    while str.endswith(bigAlphabet[-1]):
        str = str[:-1]
        k += 1
    return (str, k)


def encode(decoded):
    encoded = 0
    multiplier = 1
    for i in range(len(decoded)):
        char = decoded[i]
        try:
            index = basicAlphabet.index(char)
            if i == len(decoded) - 1 and decoded[i] == basicAlphabet[0]:
                encoded += multiplier * len(basicAlphabet)
                multiplier *= small_size_plus**2  # like adding 0
            else:
                encoded += multiplier * index
                multiplier *= small_size_plus
        except ValueError:
            encoded += multiplier * len(basicAlphabet)
            multiplier *= small_size_plus
            newid = int(i == len(decoded) - 1) + bigAlphabet.index(char)
            encoded += multiplier * newid
            multiplier *= len(bigAlphabet)
    return encoded


async def main():
    domain = encode("testingstuff")
    identity = 7943786867321230
    
    account = Account(
        address=account_address,
        client=client,
        key_pair=KeyPair.from_private_key(int(priv_key, 16)),
        chain=StarknetChainId.TESTNET,
    )
    calls = [
        Call(
            to_addr=0x0783A9097B26EAE0586373B2CE0ED3529DDC44069D1E0FBC4F66D42B69D6850D,
            selector=get_selector_from_name("mint"),
            calldata=[identity],
        ),
        Call(
            to_addr=0x049D36570D4E46F48E99674BD3FCC84644DDD6B96F7C741B1562B82F9E004DC7,
            selector=get_selector_from_name("approve"),
            calldata=[0x003BAB268E932D2CECD1946F100AE67CE3DFF9FD234119EA2F6DA57D16D29FCE, 8999999999999875, 0],
        ),
        Call(
            to_addr=0x003BAB268E932D2CECD1946F100AE67CE3DFF9FD234119EA2F6DA57D16D29FCE,
            selector=get_selector_from_name("buy"),
            calldata=[identity, domain, 365, 0, int(account_address, 16), 0, 0],
        ),
        Call(
            to_addr=0x003BAB268E932D2CECD1946F100AE67CE3DFF9FD234119EA2F6DA57D16D29FCE,
            selector=get_selector_from_name("set_address_to_domain"),
            calldata=[1, domain],
        ),
    ]
    resp = await account.execute(calls=calls, max_fee=int(1e16))
    print(f"tx_hash: {hex(resp.transaction_hash)}")

# Run the async function
asyncio.run(main())
