import io

from virustotal_python import Virustotal, VirustotalError

from Framework.GeneralUtilities import Constants, GeneralUtilities

vt = Virustotal(API_KEY=Constants.VIRUSTOTAL_API_KEY, API_VERSION="v3", TIMEOUT=30)


async def scan_text(text: str):
	RETURN_DATA = {
		"THREAT": False,
		"THREAT_NAME": None,
		"SHA256": None
	}

	# Generate a SHA256 hash from the text block
	text_hash = await GeneralUtilities.generate_sha256(text)
	RETURN_DATA["SHA256"] = text_hash

	# Check if the file has already been submitted, and if so, determine its status
	existing_file_info = await check_file_info(text_hash, RETURN_DATA)

	if existing_file_info != "NOT_FOUND":
		return existing_file_info

	# Make a file object with the text so that we can upload it
	file = io.StringIO(text)
	files = {
		"file": file
	}
	response = vt.request("files", files=files, method="POST")

	if "popular_threat_classification" in str(response.data):
		RETURN_DATA["THREAT"] = True
		if "popular_threat_name" in str(response.data):
			RETURN_DATA["THREAT_NAME"] = str(response.data["attributes"]["popular_threat_classification"]["suggested_threat_label"])
		return RETURN_DATA

	return RETURN_DATA


async def check_file_info(text_hash: str, return_data: dict):
	try:
		response = vt.request(f"files/{text_hash}")
	except VirustotalError:
		return "NOT_FOUND"

	if "popular_threat_classification" in str(response.data):
		return_data["THREAT"] = True
		if "popular_threat_name" in str(response.data):
			return_data["THREAT_NAME"] = str(
				response.data["attributes"]["popular_threat_classification"]["suggested_threat_label"])
		return return_data

	return return_data
