#
# from Ed25519-from-the-scratch (use of affine add- and double-formulas in the Montgomery Ladder)
#

# edwards25519 parameters
edwards25519_a = -1
edwards25519_d = 37095705934669439343138083508754565189542113879843219016388785533085940283555 
edwards25519_p = 2**255 - 19 # prime, order of Gallois field GF(p)
edwards25519_Gx = 15112221349535400772501151409588531511454012693041857206046113283949847762202
edwards25519_Gy = 46316835694926478169428394003475163141307993866256225615783033603165251855960
edwards25519_l = 2**252 + 27742317777372353535851937790883648493 # order of G, = order of subgroup generated by G 

def add_affine(q1, q2):
    (x1, y1) = q1
    (x2, y2) = q2
    x1x2 = (x1 * x2) % edwards25519_p
    y1y2 = (y1 * y2) % edwards25519_p
    x1y2 = (x1 * y2) % edwards25519_p
    y1x2 = (y1 * x2) % edwards25519_p
    dx1x2y1y2 = (edwards25519_d * x1x2 * y1y2) % edwards25519_p
    numerator_x = (x1y2 + y1x2) % edwards25519_p
    denominator_x_inv = pow(1 + dx1x2y1y2, -1, edwards25519_p)
    numerator_y = (y1y2 - edwards25519_a * x1x2) % edwards25519_p
    denominator_y_inv = pow(1 - dx1x2y1y2, -1, edwards25519_p)
    x3 = (numerator_x * denominator_x_inv) % edwards25519_p
    y3 = (numerator_y * denominator_y_inv) % edwards25519_p
    return (x3, y3)

def double_affine(q):
    (x1, y1) = q
    ax1x1 = (edwards25519_a * x1 * x1) % edwards25519_p
    y1y1 = (y1 * y1) % edwards25519_p
    numerator_x = (2 * x1 * y1) % edwards25519_p
    denominator_x_inv = pow(ax1x1 + y1y1, -1, edwards25519_p)
    numerator_y = (y1y1 - ax1x1) % edwards25519_p
    denominator_y_inv = pow(2 - ax1x1 - y1y1, -1, edwards25519_p)
    x3 = (numerator_x * denominator_x_inv) % edwards25519_p
    y3 = (numerator_y * denominator_y_inv) % edwards25519_p
    return (x3, y3)
  
# Montgomery Ladder, time constant for scalars up to 256 bits
def edwards25519_point_multiplication(s, p):
    q = (0, 1)                        # neutral element
    bits = bin(s)[2:]                 # bit encoding of s
    bitsPadded = bits.rjust(256, '0') # the bit representation of all scalars is extended with leading 0 to 256 bit 
    for b in bitsPadded:              # for each step, the same operations are done, no matter if the bit is 0 or 1
        if b == '0':
            p = add_affine(q, p)
            q = double_affine(q)
        else:
            q = add_affine(q, p)
            p = double_affine(p)
    return q

def clamp(le_data_b): # le_data_b in little endian order
    a_b = bytearray(le_data_b)
    a_b[0] &= 248  # 0.  byte: set the three least significant bits to 0
    a_b[31] &= 127 # 31. byte: set the most significant bit to 0
    a_b[31] |= 64  #           ...and the second-most significant bit to 1
    return bytes(a_b) 

def le_encode_to_bytes(number):
    return int.to_bytes(number, 32, "little")
  
def le_decode_to_number(number_b):
    return int.from_bytes(number_b, "little")

def decompress_point(y_b):
    y_b = bytearray(y_b) # convert to bytearray because of bit manipulations
    x_sign = (y_b[31] & 0x80 == 0x80)  # extract x sign bit
    y_b[31] = y_b[31] & ~0x80          # clear x sign bit
    y = le_decode_to_number(y_b)
    x = recover_x(y, x_sign)
    if x is None:
        return None
    else:
        return (x, y)

def recover_x(y, x_sign):
    x2 = ((y * y - 1) * pow(edwards25519_d * y * y + 1, -1, edwards25519_p)) % edwards25519_p
    x = pow(x2, (edwards25519_p + 3) // 8, edwards25519_p)
    x_final = None
    if ((x * x - x2) % edwards25519_p == 0):
        x_final = x
    elif ((x * x + x2) % edwards25519_p == 0):
        x_final = (x * pow(2, (edwards25519_p - 1) // 4, edwards25519_p)) % edwards25519_p
    else:
        return None
    if (x_final == 0) and (x_sign == 1):
        return None
    if (x_final & 1) != x_sign:
        x_final = edwards25519_p - x_final
    return x_final

#
# from X25519-from-the-scratch (use of affine add- and double-formulas in the Montgomery Ladder)
#

# curve25519 parameters
curve25519_A = 486662 
curve25519_B = 1
curve25519_p = 2**255 - 19 # prime, order of Gallois field GF(p)
curve25519_Gx = 9
curve25519_Gy = 14781619447589544791020593568409986887264606134616475288964881837755586237401
curve25519_l = 2**252 + 27742317777372353535851937790883648493 # order of G, = order of subgroup generated by G 

def curve25519_add_affine(q1, q2):
    if (q1 == q2):
        return double_affine(q1)
    if (q1 == None):
        return q2
    if (q2 == None):
        return q1
    (x1, y1) = q1
    (x2, y2) = q2
    if (x2 == x1 and y2 == -y1):
        return None
    lam_denominator_inv = pow(x1 - x2, -1, curve25519_p)
    lam = ((y1 - y2) * lam_denominator_inv) % curve25519_p 
    x3 = (curve25519_B * pow(lam, 2, curve25519_p) - curve25519_A - x1 - x2) % curve25519_p
    y3 = (lam * (x1 - x3) - y1) % curve25519_p
    return (x3, y3)

def curve25519_double_affine(q1):
    if q1 == None:
        return None
    (x1, y1) = q1
    if y1 == 0:
        return None
    lam_denominator_inv = pow(2 * curve25519_B * y1, -1, curve25519_p)
    lam = ((3 * pow(x1, 2, curve25519_p) + 2 * curve25519_A * x1 + 1) * lam_denominator_inv) % curve25519_p
    x3 = (curve25519_B * pow(lam, 2, curve25519_p) - curve25519_A - 2 * x1) % curve25519_p
    y3 = (lam * (x1 - x3) - y1) % curve25519_p
    return (x3, y3)

# Montgomery Ladder, time constant for scalars up to 256 bits
def curve25519_point_multiplication(s, p):
    q = None                            # neutral element
    bits = bin(s)[2:]                   # bit encoding of s
    bitsPadded = bits.rjust(256, '0')   # the bit representation of all scalars is extended with leading 0 to 256 bit 
    for b in bitsPadded:                # for each step, the same operations are done, no matter if the bit is 0 or 1
        if b == '0':
            p = curve25519_add_affine(q, p) 
            q = curve25519_double_affine(q)
            
        else:
            q = curve25519_add_affine(q, p) 
            p = curve25519_double_affine(p)
    return q

#
# new ###############################################################################################
# birational equivalence
#

def sqrt_minus_486664():
    a = -486664
    v = pow ((2 * a), (edwards25519_p - 5)//8, edwards25519_p)
    i = (2 * a * pow(v, 2, edwards25519_p)) % edwards25519_p 
    r = (a * v * (i - 1)) % edwards25519_p
    return r

def edwards25519_to_curve25519(ed25519_q):
    (x, y) = ed25519_q
    # u-coordinate:
    numerator_u = (1 + y) % edwards25519_p
    denominator_u_inv = pow(1 - y, -1, edwards25519_p)
    u = (numerator_u * denominator_u_inv) % edwards25519_p
    # v-coordinate
    r = sqrt_minus_486664()
    v = (r * u * pow(x, -1, edwards25519_p)) % edwards25519_p
    return (u, v)

def curve25519_to_edwards25519(curve25519_q):
    (u, v) = curve25519_q
    # x-coordinate
    r = sqrt_minus_486664()
    x = (r * u * pow(v, -1, edwards25519_p)) % edwards25519_p
    # y-coordinate
    numerator_y = (u - 1) % edwards25519_p
    denominator_y_inv = pow(u + 1, -1, edwards25519_p)
    y = (numerator_y * denominator_y_inv) % edwards25519_p
    return (x, y)

#
# Main test 1: point transformation ---------------------------------------------------------------------
# Transforms two points N, M with N=n*M on the edwars25519 curve to the curve25519 curve as N', M' with N'=n*M'
#

# edwards25519, step 1: M = m * G
from secrets import randbelow
edwards25519_m = randbelow(edwards25519_l)
edwards25519_M = edwards25519_point_multiplication(edwards25519_m, (edwards25519_Gx, edwards25519_Gy))
print("m: " + str(edwards25519_m))
print("edwards25519_M: " + str(edwards25519_M))

# edwards25519, step 1: N = n * M
edwards25519_n = randbelow(edwards25519_l)
edwards25519_N = edwards25519_point_multiplication(edwards25519_n, edwards25519_M)
print("n: " + str(edwards25519_n))
print("edwards25519_N: " + str(edwards25519_N))

print()

# transformation edwards25519 -> curve25519
curve25519_M = edwards25519_to_curve25519(edwards25519_M)
curve25519_N = edwards25519_to_curve25519(edwards25519_N)
print("curve25519_M: " + str(curve25519_M))
print("curve25519_N: " + str(curve25519_N))

print()

# consistency check 1: Back transformation curve25519 -> edwards25519
edwards25519_M_reloaded = curve25519_to_edwards25519(curve25519_M)
edwards25519_N_reloaded = curve25519_to_edwards25519(curve25519_N)
print("edwards25519_M: " + str(edwards25519_M_reloaded))
print("edwards25519_N: " + str(edwards25519_N_reloaded))

print()

# consistency check 2: Check N' = n * M' 
curve25519_N_directly = curve25519_point_multiplication(edwards25519_n, curve25519_M)
print("edwards25519_N: " + str(curve25519_N))
print("edwards25519_N: " + str(curve25519_N_directly))

#
# Main test 2: key transformation ---------------------------------------------------------------------
# Transforms an Ed25519 keypair to an X25519 keypair
#

'''
Ed25519 key pair from Ed25519-from-the-scratch/500_key_generation.py
private: 925774cba2b5900e4594d5c7596f45c0ccda2ae126cb3bb0e5a88f9eb07772d1
public:  b0817e76a295e28feb8e4cbbe1f51adcb23fbf9e82b2b4c56f115601b9ee2c11
'''

print()

# transform secret key
import hashlib
ed25519_secret_key = bytes.fromhex("925774cba2b5900e4594d5c7596f45c0ccda2ae126cb3bb0e5a88f9eb07772d1")
s = hashlib.sha512(ed25519_secret_key).digest()[:32]
x25519_secret_key = clamp(s)                              

# transform public key
ed25519_public_key = bytes.fromhex("b0817e76a295e28feb8e4cbbe1f51adcb23fbf9e82b2b4c56f115601b9ee2c11")
ed25519_public_key_decompressed = decompress_point(ed25519_public_key)
x25519_public_key_complete = edwards25519_to_curve25519(ed25519_public_key_decompressed)
x25519_public_key = le_encode_to_bytes(x25519_public_key_complete[0]) # x-coordinate

print("X25519 secret key (transformed): " + x25519_secret_key.hex())
print("X25519 public key (transformed): " + x25519_public_key.hex())

# consistency check:
# x25519_public_key = x25519_secret_key * G
G = (curve25519_Gx, curve25519_Gy)
x25519_secret_key_int = le_decode_to_number(x25519_secret_key)
x25519_public_key_via_mult_int = curve25519_point_multiplication(x25519_secret_key_int, G)[0] # x-coordinate
x25519_public_key_via_mult = le_encode_to_bytes(x25519_public_key_via_mult_int)
print("X25519 public key (via mult.)  : " + x25519_public_key_via_mult.hex())

'''
# consistency-check with PHP/sodium
<?php
$ed25519_keypair = sodium_crypto_sign_seed_keypair(hex2bin("925774cba2b5900e4594d5c7596f45c0ccda2ae126cb3bb0e5a88f9eb07772d1"));
$ed25519_sec = substr($ed25519_keypair, 0, 64);
$ed25519_pub = substr($ed25519_keypair, 64);
print("sec|pub|pub: " . bin2hex($ed25519_keypair) . "\n");
print("sec|pub    : " . bin2hex($ed25519_sec) . "\n");
print("pub        : " . bin2hex($ed25519_pub) . "\n");
print("\n");

$x25519_sec = sodium_crypto_sign_ed25519_sk_to_curve25519($ed25519_sec);
$x25519_pub = sodium_crypto_sign_ed25519_pk_to_curve25519($ed25519_pub);
print("sec        : " . bin2hex($x25519_sec) . "\n");
print("pub        : " . bin2hex($x25519_pub) . "\n");
?>

sec|pub|pub: 925774cba2b5900e4594d5c7596f45c0ccda2ae126cb3bb0e5a88f9eb07772d1b0817e76a295e28feb8e4cbbe1f51adcb23fbf9e82b2b4c56f115601b9ee2c11b0817e76a295e28feb8e4cbbe1f51adcb23fbf9e82b2b4c56f115601b9ee2c11
sec|pub    : 925774cba2b5900e4594d5c7596f45c0ccda2ae126cb3bb0e5a88f9eb07772d1b0817e76a295e28feb8e4cbbe1f51adcb23fbf9e82b2b4c56f115601b9ee2c11
pub        : b0817e76a295e28feb8e4cbbe1f51adcb23fbf9e82b2b4c56f115601b9ee2c11

sec        : c0ab9b08992ff21361cd5ad402c813787a136c78a29508e4244948bba1c0664d
pub        : 1aadb0b40cfd3388c578108b4bf0c91fa30f35c3eb90d5ec159ad1f217ed5b7e
'''
