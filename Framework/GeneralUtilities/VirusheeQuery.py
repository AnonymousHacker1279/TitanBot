from hashlib import sha256


async def generate_sha256(string: str) -> str:
	return sha256(string.encode('utf-8')).hexdigest()
