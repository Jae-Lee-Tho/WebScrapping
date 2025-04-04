🧠 Mnemonic Generator Scraper

This project scrapes mnemonic content from the Mammoth Memory website using Selenium and BeautifulSoup to create a structured dataset for training a multilingual and multimodal mnemonic generation model.

📌 What This Script Does
	•	Takes in a URL from the Mammoth Memory website.
	•	Extracts the following:
	•	✅ Words/concept pairs (e.g., chemical element + symbol)
	•	✅ Associated mnemonic text
	•	✅ Highlighted red text (often used to emphasize keywords)
	•	✅ Image URLs used in visual mnemonics
	•	✅ Captions related to images (included in the dataset)

The extracted content is saved in a structured JSON format (result.json), ready for use in downstream training or analysis.

🧪 Technologies Used
	•	Selenium (with headless Chrome) – for dynamic webpage interaction and rendering
	•	BeautifulSoup – for HTML parsing and data extraction
	•	re (Regex) – for HTML cleanup and string processing
	•	json – for data output
