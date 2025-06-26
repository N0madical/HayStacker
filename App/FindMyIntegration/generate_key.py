#####
# Key generator for HayStacker, based on Biemster's FindMy project
# Adapted by Aiden C
#####

import os,base64,hashlib,random, pathlib
import platform

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

def getKeysDir() -> pathlib.Path:
    """
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = pathlib.Path.home()

    if platform.system() == "Windows":
        return home / "AppData/Local/HayStacker/keys"
    elif platform.system() == "Linux":
        return home / ".local/share/HayStacker/keys"
    elif platform.system() == "Darwin":
        return home / "Library/Application Support/HayStacker/keys"
    else:
        return pathlib.Path(__file__).parent.resolve() / "keys"

# SHA256 Algorithim Wrapper
def sha256(data):
    digest = hashlib.new("sha256")
    digest.update(data)
    return digest.digest()

# Function to write a file with the desired key name
def writeKey(name):
    priv = random.getrandbits(224)
    adv = ec.derive_private_key(priv, ec.SECP224R1(), default_backend()).public_key().public_numbers().x

    priv_bytes = int.to_bytes(priv, 28, 'big')
    adv_bytes = int.to_bytes(adv, 28, 'big')

    priv_b64 = base64.b64encode(priv_bytes).decode("ascii")
    adv_b64 = base64.b64encode(adv_bytes).decode("ascii")
    s256_b64 = base64.b64encode(sha256(adv_bytes)).decode("ascii")

    if '/' in s256_b64[:7] or '\\' in s256_b64[:7]:
        print('there was a / in the b64 of the hashed pubkey :(, retrying')
        writeKey(name)
    else:
        fpath = getKeysDir()
        fname = os.path.join(fpath, f"{name}.keys")
        print(f'Writing {fname}')

        with open(fname, 'w') as f:
            f.write('Private key: %s\n' % priv_b64)
            f.write('Advertisement key: %s\n' % adv_b64)
            f.write('Hashed adv key: %s\n' % s256_b64)
