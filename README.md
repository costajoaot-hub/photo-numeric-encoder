# photo-numeric-encoder
A Python script that renames photos using random and unique numeric encoding.

Photo Anonymizer & Audit Tool
This Python-based tool was developed to automate the anonymization and auditing process for photography contests or data collection.

It bridges the gap between raw data stored in Excel and physical files, ensuring each entry is correctly identified, renamed with a unique random code, and documented for a blind jury review.

Features
Automated Anonymization: Generates unique, non-repeating 3-digit random codes (111-999) for each file.

Data Integrity Audit: Compares Excel records with local files and identifies:
Successfully processed files.
Missing files (links in Excel without matching local files).
Orphan files (files in the folder that don't match any Excel record).
Smart Matching: Includes a fallback logic to match files even if filenames are slightly truncated or contain URL-encoded characters.
Metadata Preservation: Uses shutil.copy2 to preserve original file metadata (timestamps) during the process.

Technologies & Libraries
Python 3.x
Pandas: For Excel data manipulation.
OS & Shutil: For file system operations and secure copying.
Random: For generating unique anonymous IDs.
Urllib: To handle complex URL-encoded filenames from web forms.
