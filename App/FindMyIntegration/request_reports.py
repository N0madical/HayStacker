#!/usr/bin/env python3
import os,glob,datetime,time
import base64,json
import hashlib,struct
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import ec
import sqlite3
from os.path import dirname, join, abspath
from .pypush_gsa_icloud import icloud_login_mobileme, generate_anisette_headers, reset_headers
from tkinter import messagebox
from FindMyIntegration.generate_key import getKeysDir

retryFunc = None
retryCount = 0

def setRetryFunc(funcIn):
    global retryFunc
    retryFunc = funcIn

def sha256(data):
    digest = hashlib.new("sha256")
    digest.update(data)
    return digest.digest()

def decrypt(enc_data, algorithm_dkey, mode):
    decryptor = Cipher(algorithm_dkey, mode).decryptor()
    return decryptor.update(enc_data) + decryptor.finalize()

def decode_tag(data):
    latitude = struct.unpack(">i", data[0:4])[0] / 10000000.0
    longitude = struct.unpack(">i", data[4:8])[0] / 10000000.0
    confidence = int.from_bytes(data[8:9], 'big')
    status = int.from_bytes(data[9:10], 'big')
    return {'lat': latitude, 'lon': longitude, 'conf': confidence, 'status':status}

def getAuth(username='', password='', regenerate=False, second_factor='sms'):
    CONFIG_PATH = abspath("auth.json")
    if os.path.exists(CONFIG_PATH) and not regenerate:
        with open(CONFIG_PATH, "r") as f: j = json.load(f)
    else:
        mobileme = icloud_login_mobileme(username, password, second_factor=second_factor)
        j = {'dsid': mobileme['dsid'], 'searchPartyToken': mobileme['delegates']['com.apple.mobileme']['service-data']['tokens']['searchPartyToken']}
        with open(CONFIG_PATH, "w") as f: json.dump(j, f)
    return (j['dsid'], j['searchPartyToken'])


def request_reports(anisette, username='', password='', useSMS=False, hours=24, regen=False):
    global retryCount
    global retryFunc

    try:
        try:
            sq3db = sqlite3.connect(abspath("reports.db"), timeout=10)
            sq3 = sq3db.cursor()
        except Exception as e:
            messagebox.showerror("Error connecting to local database (reports.db). Is it in use?")
            print("Sqlite error: ", e)

        privkeys = {}
        names = {}
        for keyfile in glob.glob(join(getKeysDir(), '*.keys')):
            # read key files generated with generate_keys.py
            with open(keyfile) as f:
                hashed_adv = priv = ''
                name = os.path.basename(keyfile)[0:-5]
                for line in f:
                    key = line.strip().split(': ')
                    if key[0] == 'Private key': priv = key[1]
                    elif key[0] == 'Hashed adv key': hashed_adv = key[1]

                if priv and hashed_adv:
                    privkeys[hashed_adv] = priv
                    names[hashed_adv] = name
                else: print(f"Couldn't find key pair in {keyfile}")

        unixEpoch = int(time.time())
        startdate = unixEpoch - (60 * 60 * hours)
        data = { "search": [{"startDate": startdate *1000, "endDate": unixEpoch *1000, "ids": list(names.keys())}] }

        r = requests.post("https://gateway.icloud.com/acsnservice/fetch",
                auth=getAuth(username, password, regenerate=regen, second_factor='trusted_device' if not useSMS else 'sms'),
                headers=generate_anisette_headers(),
                json=data)
        print(r)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            if r.status_code == 401:
                if retryCount < 3:
                    reset_headers()
                    retryCount += 1
                    retryFunc(False)
                    return
                else:
                    retryFunc(True)
                    return
            else:
                print(f"HTTP error: {e}")
                messagebox.showerror("Network error", f"Network error: {e}")
        res = json.loads(r.content.decode())['results']
        print(f'{r.status_code}: {len(res)} reports received.')

        ordered = []
        found = set()
        for report in res:
            priv = int.from_bytes(base64.b64decode(privkeys[report['id']]), 'big')
            data = base64.b64decode(report['payload'].replace('\n', '').replace('\r', ''))
            if len(data) > 88: data = data[:4] + data[5:]

            # the following is all copied from https://github.com/hatomist/openhaystack-python, thanks @hatomist!
            timestamp = int.from_bytes(data[0:4], 'big') +978307200
            # sq3.execute(f"INSERT OR REPLACE INTO reports VALUES ('{names[report['id']]}', {timestamp}, {report['datePublished']}, '{report['payload']}', '{report['id']}', {report['statusCode']})")
            if timestamp >= startdate:
                eph_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP224R1(), data[5:62])
                shared_key = ec.derive_private_key(priv, ec.SECP224R1()).exchange(ec.ECDH(), eph_key)
                symmetric_key = sha256(shared_key + b'\x00\x00\x00\x01' + data[5:62])
                decryption_key = symmetric_key[:16]
                iv = symmetric_key[16:]
                enc_data = data[62:72]
                tag = data[72:]

                decrypted = decrypt(enc_data, algorithms.AES(decryption_key), modes.GCM(iv, tag))
                tag = decode_tag(decrypted)
                tag['timestamp'] = timestamp
                tag['isodatetime'] = datetime.datetime.fromtimestamp(timestamp).isoformat()
                tag['key'] = names[report['id']]
                tag['goog'] = 'https://maps.google.com/maps?q=' + str(tag['lat']) + ',' + str(tag['lon'])
                found.add(tag['key'])
                ordered.append(tag)
        print(f'{len(ordered)} reports used.')
        ordered.sort(key=lambda item: item.get('timestamp'))
        print("Found reports:")
        for rep in ordered: print(f"('{rep['key']}', {rep['timestamp']}, '{rep['isodatetime']}', '{rep['lat']}', '{rep['lon']}', '{rep['goog']}', {rep['status']}, {rep['conf']})")
        for rep in ordered: sq3.execute(f"INSERT OR REPLACE INTO reports VALUES ('{rep['key']}', {rep['timestamp']}, '{rep['isodatetime']}', '{rep['lat']}', '{rep['lon']}', '{rep['goog']}', {rep['status']}, {rep['conf']})")
        print(f'found:   {list(found)}')
        print(f'missing: {[key for key in names.values() if key not in found]}')
        sq3.close()
        sq3db.commit()
        sq3db.close()
        retryCount = 0
    except Exception as e:
        print("Error getting reports:")
        raise e
    finally:
        anisette.terminate()