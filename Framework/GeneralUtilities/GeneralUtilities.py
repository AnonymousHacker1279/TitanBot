import subprocess
from hashlib import sha256

import nest_asyncio

nest_asyncio.apply()


async def generate_sha256(string: str) -> str:
	return sha256(string.encode('utf-8')).hexdigest()


def generate_sha256_no_async(string: str) -> str:
	return sha256(string.encode('utf-8')).hexdigest()


def get_git_revision_short_hash() -> str:
	return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
