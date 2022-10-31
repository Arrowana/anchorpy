"""Contains code for parsing the IDL file."""
from dataclasses import dataclass, field
from typing import List, Union, Optional, Dict, Any, Literal, Tuple, TypedDict, Sequence
from anchorpy_core.idl import IdlTypeDefinition

from apischema import deserialize, alias
from apischema.metadata import conversion
from pyheck import snake, upper_camel
from borsh_construct import CStruct, Vec, U8
import solana.publickey  # noqa: WPS301

from anchorpy.borsh_extension import BorshPubkey

# We have to define these wrappers because snake and upper_camel
# don't have annotations
def _underscore(s: str) -> str:
    return snake(s)


def _camelize(s: str) -> str:
    return upper_camel(s)


snake_case_conversion = conversion(_underscore, _camelize)

def _idl_address(program_id: solana.publickey.PublicKey) -> solana.publickey.PublicKey:
    """Deterministic IDL address as a function of the program id.

    Args:
        program_id: The program ID.

    Returns:
        The public key of the IDL.
    """
    base = solana.publickey.PublicKey.find_program_address([], program_id)[0]
    return solana.publickey.PublicKey.create_with_seed(base, "anchor:idl", program_id)


class IdlProgramAccount(TypedDict):
    """The on-chain account of the IDL."""

    authority: solana.publickey.PublicKey
    data: bytes


IDL_ACCOUNT_LAYOUT = CStruct("authority" / BorshPubkey, "data" / Vec(U8))


def _decode_idl_account(data: bytes) -> IdlProgramAccount:
    """Decode on-chain IDL.

    Args:
        data: binary data from the account that stores the IDL.

    Returns:
        Decoded IDL.
    """
    return IDL_ACCOUNT_LAYOUT.parse(data)


TypeDefs = Sequence[IdlTypeDefinition]
