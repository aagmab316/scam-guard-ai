import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import analyze_text

print(analyze_text("URGENT: Your account will be suspended in 24 hours. Verify at http://bit.ly/secure-login and send your verification code."))
