import io

import vt

from Framework.GeneralUtilities import Constants, GeneralUtilities

vt_client = vt.Client(Constants.VIRUSTOTAL_API_KEY)


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
	try:
		response = await vt_client.get_object_async("/files/" + text_hash)
		RETURN_DATA = await check_results(response, RETURN_DATA, True)

		return RETURN_DATA
	except vt.APIError:
		# Make a file object with the text so that we can upload it for scanning
		file = io.StringIO(text)
		response = await vt_client.scan_file_async(file, wait_for_completion=True)

		return await check_results(response, RETURN_DATA, False)


async def check_results(response, return_data: dict, check_previous_submissions: bool):
	if check_previous_submissions:
		analysis_stats = response.get("last_analysis_stats")
	else:
		analysis_stats = response.get("stats")
	if analysis_stats["malicious"] != 0 or analysis_stats["suspicious"] != 0:
		return_data["THREAT"] = True
		return_data["THREAT_NAME"] = response.get("popular_threat_classification")["suggested_threat_label"]

	return return_data
