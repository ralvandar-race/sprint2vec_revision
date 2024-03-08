import re

def preprocess_sebert(text):
    """
    1) Basic preprocessing: 
    We convert all documents to lowercase, 
    remove control characters (newline, carriage return, tab),
    and normalize quotation marks and whitespaces.
    """
    text = text.lower()
    text = re.sub(r'[\n\r\t]', ' ', text)
    text = re.sub(r'[‘’“”]', '"', text)
    text = re.sub(r'\s+', ' ', text).strip()

    """
    5) Hashes: Hashes such as SHA-1 or md5 
    do not provide any contextual information and should be removed. 
    We detect hashes by checking whether alphanumeric words 
    with a length of 7 characters or more can be cast to a hexadecimal number and replace.
    """
    hash_pattern = re.compile(r'\b(?:[a-fA-F0-9]{7,})\b')
    text = re.sub(hash_pattern, ' ', text)

    """
    6) Code: Source code is not natural language and should be removed. 
    However, finding code fragments within text is a non-trivial task. 
    We use HTML <code> tags, Markdown code blocks, and other formatting 
    to identify source code and replace it with [CODE] tokens. 
    Code that is not within such environments.
    """
    html_code_pattern = re.compile(r'<code>.*?</code>', re.DOTALL)
    other_code_pattern = re.compile(r'{code}.*?{code}', re.DOTALL)
    markdown_code_pattern = re.compile(r'```.*?```', re.DOTALL)
    text = re.sub(html_code_pattern, '[CODE]', text)
    text = re.sub(markdown_code_pattern, '[CODE]', text)
    text = re.sub(other_code_pattern, '[CODE]', text)

    """
    8) Special formatting: We remove special formatting and content such as 
    Jira specific formatting, Git sign-off, or references to SVN.
    Remove patterns in the format [<text>-<number>].
    """
    text = re.sub(r'\[[\w\s]+-\d+\]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text